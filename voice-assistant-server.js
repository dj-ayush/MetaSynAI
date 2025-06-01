const express = require('express');
const fileUpload = require('express-fileupload');
const path = require('path');
const fs = require('fs');
const pdf = require('pdf-parse');
const textToSpeech = require('text-to-speech-js');
const cors = require('cors');

// Initialize Express app
const app = express();
app.use(cors());
app.use(express.json());
app.use(fileUpload({
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB
  abortOnLimit: true
}));
app.use(express.static('public'));

// In-memory database (for simplicity, replace with real DB in production)
const filesDB = [];
const userSessions = {};

// Configuration
const config = {
  allowedFileTypes: ['application/pdf', 'application/msword', 
                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  maxFileSize: 100 * 1024 * 1024 // 100MB
};

// Helper function to extract text from PDF
async function extractTextFromPDF(dataBuffer) {
  try {
    const data = await pdf(dataBuffer);
    return data.text;
  } catch (err) {
    console.error('Error extracting text from PDF:', err);
    throw new Error('Failed to extract text from PDF');
  }
}

// Process voice commands
function processVoiceCommand(command, content, sessionId) {
  const commands = content.split('\n').filter(cmd => cmd.trim() !== '');
  const totalPages = commands.length;
  
  // Initialize or get user session
  if (!userSessions[sessionId]) {
    userSessions[sessionId] = {
      currentPage: 0,
      isReading: false,
      lastPosition: 0
    };
  }
  
  const session = userSessions[sessionId];
  let response = {};

  command = command.toLowerCase().trim();

  switch (command) {
    case 'zoom in':
      response = {
        action: 'zoom',
        level: 'in',
        message: 'Zooming in'
      };
      break;
    case 'zoom out':
      response = {
        action: 'zoom',
        level: 'out',
        message: 'Zooming out'
      };
      break;
    case 'next page':
    case 'right swipe':
      session.currentPage = Math.min(session.currentPage + 1, totalPages - 1);
      session.lastPosition = 0;
      response = {
        action: 'navigate',
        direction: 'next',
        content: commands[session.currentPage],
        currentPage: session.currentPage,
        totalPages,
        message: `Page ${session.currentPage + 1} of ${totalPages}`
      };
      break;
    case 'previous page':
    case 'left swipe':
      session.currentPage = Math.max(session.currentPage - 1, 0);
      session.lastPosition = 0;
      response = {
        action: 'navigate',
        direction: 'previous',
        content: commands[session.currentPage],
        currentPage: session.currentPage,
        totalPages,
        message: `Page ${session.currentPage + 1} of ${totalPages}`
      };
      break;
    case 'read':
    case 'start reading':
      session.isReading = true;
      const contentToRead = commands.slice(session.currentPage).join('\n');
      response = {
        action: 'read',
        content: contentToRead,
        currentPage: session.currentPage,
        totalPages,
        message: `Starting to read from page ${session.currentPage + 1}`
      };
      textToSpeech.synthesize(contentToRead, {
        amplitude: 100,
        wordgap: 0,
        pitch: 50,
        speed: 175
      });
      break;
    case 'continue reading':
      session.isReading = true;
      const remainingContent = commands[session.currentPage].substring(session.lastPosition) + 
                             commands.slice(session.currentPage + 1).join('\n');
      response = {
        action: 'read',
        content: remainingContent,
        currentPage: session.currentPage,
        totalPages,
        message: `Continuing from page ${session.currentPage + 1}`
      };
      textToSpeech.synthesize(remainingContent, {
        amplitude: 100,
        wordgap: 0,
        pitch: 50,
        speed: 175
      });
      break;
    case 'pause':
    case 'stop reading':
      session.isReading = false;
      session.lastPosition = 0;
      response = {
        action: 'pause',
        message: 'Reading paused',
        currentPage: session.currentPage
      };
      textToSpeech.cancel();
      break;
    case 'stop':
    case 'close':
      session.isReading = false;
      response = {
        action: 'stop',
        message: 'Voice assistant stopped'
      };
      textToSpeech.cancel();
      break;
    default:
      response = {
        action: 'unknown',
        message: "Sorry, I didn't get that. Please try again."
      };
  }

  return response;
}

// Routes
app.post('/api/voice/upload', async (req, res) => {
  try {
    if (!req.files || Object.keys(req.files).length === 0) {
      return res.status(400).json({ success: false, message: 'No files were uploaded.' });
    }

    const file = req.files.file;

    // Check file type
    if (!config.allowedFileTypes.includes(file.mimetype)) {
      return res.status(400).json({ success: false, message: 'Invalid file type. Only PDF and Word documents are allowed.' });
    }

    // Create uploads directory if it doesn't exist
    if (!fs.existsSync('./uploads')) {
      fs.mkdirSync('./uploads');
    }

    // Extract text from PDF
    let fileContent = '';
    if (file.mimetype === 'application/pdf') {
      fileContent = await extractTextFromPDF(file.data);
    } else {
      fileContent = 'Word document content extraction not implemented yet.';
    }

    // Save file to uploads folder
    const uploadPath = path.join(__dirname, 'uploads', file.name);
    await file.mv(uploadPath);

    // Save file info to database
    const newFile = {
      id: Date.now().toString(),
      filename: file.name,
      path: uploadPath,
      size: file.size,
      mimetype: file.mimetype,
      content: fileContent,
      createdAt: new Date()
    };

    filesDB.push(newFile);

    res.status(200).json({
      success: true,
      message: 'File uploaded successfully',
      file: {
        id: newFile.id,
        name: newFile.filename,
        size: newFile.size,
        content: newFile.content
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ 
      success: false,
      message: err.message || 'Server error during file upload'
    });
  }
});

app.post('/api/voice/command', async (req, res) => {
  try {
    const { command, fileId, sessionId } = req.body;

    if (!command || !fileId || !sessionId) {
      return res.status(400).json({ 
        success: false,
        message: 'Command, file ID and session ID are required' 
      });
    }

    const file = filesDB.find(f => f.id === fileId);
    if (!file) {
      return res.status(404).json({ 
        success: false,
        message: 'File not found' 
      });
    }

    const response = processVoiceCommand(command, file.content, sessionId);

    res.status(200).json({
      success: true,
      ...response
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ 
      success: false,
      message: err.message || 'Server error processing command'
    });
  }
});

app.get('/api/voice/file/:id', async (req, res) => {
  try {
    const file = filesDB.find(f => f.id === req.params.id);
    if (!file) {
      return res.status(404).json({ 
        success: false,
        message: 'File not found' 
      });
    }

    res.status(200).json({
      success: true,
      file
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ 
      success: false,
      message: 'Server error retrieving file'
    });
  }
});

// Serve the HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'voice-assistant.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: 'Internal server error'
  });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Access the application at: http://localhost:${PORT}`);
});