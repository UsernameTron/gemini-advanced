import express, { Request, Response } from 'express';
import { createServer as createHttpServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import multer from 'multer';
import { join } from 'path';
import { RetroImageEngine } from './image-engine';
import { EnhancedCommandProcessor } from './command-processor';

interface ServerConfig {
  imageEngine: RetroImageEngine;
  commandProcessor: EnhancedCommandProcessor;
}

export async function createServer(config: ServerConfig) {
  const app = express();
  const httpServer = createHttpServer(app);
  const io = new Server(httpServer, {
    cors: {
      origin: "*",
      methods: ["GET", "POST"]
    }
  });

  // Middleware
  app.use(cors());
  app.use(express.json({ limit: '50mb' }));
  app.use(express.urlencoded({ extended: true, limit: '50mb' }));

  // Serve static files
  app.use(express.static(join(__dirname, '../renderer')));
  app.use('/assets', express.static(join(__dirname, '../../assets')));

  // Configure multer for file uploads
  const upload = multer({
    dest: 'uploads/',
    limits: {
      fileSize: 10 * 1024 * 1024 // 10MB limit
    }
  });

  // API Routes
  app.get('/api/health', (req: Request, res: Response) => {
    res.json({ 
      status: 'ok', 
      timestamp: new Date().toISOString(),
      service: 'Retro AI Desktop',
      version: '1.0.0'
    });
  });

  app.get('/', (req: Request, res: Response) => {
    res.sendFile(join(__dirname, '../renderer/index.html'));
  });

  app.post('/api/command', async (req: Request, res: Response) => {
    try {
      const { command } = req.body;
      const result = await config.commandProcessor.processCommand(command);
      res.json({ success: true, result });
    } catch (error) {
      console.error('Command processing error:', error);
      res.status(500).json({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  app.post('/api/upload', upload.single('image'), async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        res.status(400).json({ success: false, error: 'No file uploaded' });
        return;
      }

      const imagePath = req.file.path;
      // Process the uploaded image
      const result = await config.imageEngine.processUpload(imagePath);
      
      res.json({ success: true, result });
    } catch (error) {
      console.error('Upload processing error:', error);
      res.status(500).json({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Upload failed'
      });
    }
  });

  app.get('/api/status', (req: Request, res: Response) => {
    res.json({
      success: true,
      status: {
        imageEngine: !!config.imageEngine,
        commandProcessor: !!config.commandProcessor,
        timestamp: new Date().toISOString()
      }
    });
  });

  app.get('/api/gallery', async (req: Request, res: Response) => {
    try {
      const gallery = await config.imageEngine.getGallery();
      res.json({ success: true, gallery });
    } catch (error) {
      console.error('Gallery retrieval error:', error);
      res.status(500).json({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Gallery retrieval failed'
      });
    }
  });

  // Socket.IO for real-time communication
  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);

    socket.on('command', async (data) => {
      try {
        const result = await config.commandProcessor.processCommand(data.command);
        socket.emit('command-result', { success: true, result });
      } catch (error) {
        socket.emit('command-result', { 
          success: false, 
          error: error instanceof Error ? error.message : 'Command failed'
        });
      }
    });

    socket.on('image-upload', async (data) => {
      try {
        const result = await config.imageEngine.processImageData(data);
        socket.emit('image-result', { success: true, result });
      } catch (error) {
        socket.emit('image-result', { 
          success: false, 
          error: error instanceof Error ? error.message : 'Image processing failed'
        });
      }
    });

    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
    });
  });

  // Start server
  return new Promise((resolve, reject) => {
    const port = process.env.PORT || 3001;
    httpServer.listen(port, () => {
      console.log(`Retro AI Desktop server running on http://localhost:${port}`);
      resolve(httpServer);
    }).on('error', reject);
  });
}
