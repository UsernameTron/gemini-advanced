import { GoogleGenerativeAI } from '@google/generative-ai';
import { promises as fs } from 'fs';
import { join } from 'path';

interface ImageGenerationResult {
  success: boolean;
  images?: string[];
  text?: string;
  sessionId?: string;
  error?: string;
}

interface EditingSession {
  id: string;
  original: string;
  current: string;
  history: string[];
  prompts: string[];
  timestamp: Date;
}

export class RetroImageEngine {
  private genAI!: GoogleGenerativeAI;
  private editingSessions: Map<string, EditingSession> = new Map();
  private gallery: string[] = [];
  private initialized = false;

  constructor() {
    this.initializeModels();
  }

  private async initializeModels(): Promise<void> {
    try {
      const apiKey = process.env.GOOGLE_API_KEY;
      if (!apiKey) {
        throw new Error('GOOGLE_API_KEY environment variable is required');
      }

      this.genAI = new GoogleGenerativeAI(apiKey);
      this.initialized = true;
      console.log('✅ Gemini & Imagen models initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize AI models:', error);
      throw error;
    }
  }

  async generateWithGemini(prompt: string): Promise<ImageGenerationResult> {
    if (!this.initialized) {
      throw new Error('Image engine not initialized');
    }

    try {
      const model = this.genAI.getGenerativeModel({ 
        model: "gemini-2.0-flash-exp" 
      });

      const enhancedPrompt = `Generate a high-quality image: ${prompt}. 
        Make it detailed, professional, and visually appealing.`;

      const result = await model.generateContent([enhancedPrompt]);
      const response = await result.response;
      const text = response.text();

      // For now, return text response with image placeholder
      // In a real implementation, you'd process the actual image generation
      const imageId = this.generateImageId();
      const imagePath = await this.saveGeneratedImage(text, imageId, 'gemini');

      this.gallery.push(imagePath);

      return {
        success: true,
        images: [imagePath],
        text: text,
        sessionId: imageId
      };
    } catch (error) {
      console.error('Gemini generation error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Gemini generation failed'
      };
    }
  }

  async generateWithImagen(prompt: string, options: any = {}): Promise<ImageGenerationResult> {
    if (!this.initialized) {
      throw new Error('Image engine not initialized');
    }

    try {
      // Enhanced prompt for Imagen
      const enhancedPrompt = this.enhanceImagenPrompt(prompt, options);
      
      // Simulate Imagen generation (replace with actual API call)
      const imageId = this.generateImageId();
      const imagePath = await this.saveGeneratedImage(enhancedPrompt, imageId, 'imagen');

      this.gallery.push(imagePath);

      return {
        success: true,
        images: [imagePath],
        text: `Generated with Imagen: ${prompt}`,
        sessionId: imageId
      };
    } catch (error) {
      console.error('Imagen generation error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Imagen generation failed'
      };
    }
  }

  async editImage(sessionId: string, editPrompt: string, imagePath?: string): Promise<ImageGenerationResult> {
    try {
      let session = this.editingSessions.get(sessionId);
      
      if (!session && imagePath) {
        // Create new editing session
        session = {
          id: sessionId,
          original: imagePath,
          current: imagePath,
          history: [],
          prompts: [],
          timestamp: new Date()
        };
        this.editingSessions.set(sessionId, session);
      }

      if (!session) {
        throw new Error('No editing session found. Upload an image first.');
      }

      // Apply edit (simplified for demonstration)
      const newImageId = this.generateImageId();
      const editedImagePath = await this.applyEdit(session.current, editPrompt, newImageId);

      // Update session
      session.history.push(session.current);
      session.current = editedImagePath;
      session.prompts.push(editPrompt);

      this.gallery.push(editedImagePath);

      return {
        success: true,
        images: [editedImagePath],
        text: `Applied edit: ${editPrompt}`,
        sessionId: sessionId
      };
    } catch (error) {
      console.error('Image editing error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Image editing failed'
      };
    }
  }

  async processUpload(filePath: string): Promise<{ sessionId: string; path: string }> {
    const sessionId = this.generateImageId();
    
    // Copy uploaded file to our managed directory
    const targetPath = join(__dirname, '../../uploads', `${sessionId}_original.jpg`);
    await fs.copyFile(filePath, targetPath);
    
    // Create editing session
    const session: EditingSession = {
      id: sessionId,
      original: targetPath,
      current: targetPath,
      history: [],
      prompts: [],
      timestamp: new Date()
    };
    
    this.editingSessions.set(sessionId, session);
    
    return { sessionId, path: targetPath };
  }

  async processImageData(data: any): Promise<ImageGenerationResult> {
    // Handle base64 image data from the frontend
    const { imageData, command, sessionId } = data;
    
    if (command === 'upload') {
      const imagePath = await this.saveBase64Image(imageData);
      const session = await this.processUpload(imagePath);
      return {
        success: true,
        sessionId: session.sessionId,
        text: 'Image uploaded successfully'
      };
    }
    
    return { success: false, error: 'Unknown image command' };
  }

  async getGallery(): Promise<string[]> {
    return this.gallery;
  }

  private enhanceImagenPrompt(prompt: string, options: any): string {
    let enhanced = prompt;
    
    if (options.style) {
      enhanced += `, ${options.style} style`;
    }
    
    if (options.quality) {
      enhanced += `, ${options.quality} quality`;
    }
    
    if (options.aspectRatio) {
      enhanced += `, ${options.aspectRatio} aspect ratio`;
    }
    
    return enhanced;
  }

  private generateImageId(): string {
    return `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async saveGeneratedImage(content: string, imageId: string, model: string): Promise<string> {
    // Create a placeholder image with the generation details
    const imagePath = join(__dirname, '../../generated', `${imageId}_${model}.json`);
    
    // Ensure directory exists
    await fs.mkdir(join(__dirname, '../../generated'), { recursive: true });
    
    const imageData = {
      id: imageId,
      model: model,
      prompt: content,
      timestamp: new Date().toISOString(),
      type: 'generated'
    };
    
    await fs.writeFile(imagePath, JSON.stringify(imageData, null, 2));
    return imagePath;
  }

  private async applyEdit(imagePath: string, editPrompt: string, newImageId: string): Promise<string> {
    // Simulate image editing (replace with actual implementation)
    const editedPath = join(__dirname, '../../generated', `${newImageId}_edited.json`);
    
    const editData = {
      id: newImageId,
      originalPath: imagePath,
      editPrompt: editPrompt,
      timestamp: new Date().toISOString(),
      type: 'edited'
    };
    
    await fs.writeFile(editedPath, JSON.stringify(editData, null, 2));
    return editedPath;
  }

  private async saveBase64Image(base64Data: string): Promise<string> {
    const imageId = this.generateImageId();
    const imagePath = join(__dirname, '../../uploads', `${imageId}.jpg`);
    
    // Remove data URL prefix if present
    const base64 = base64Data.replace(/^data:image\/[a-z]+;base64,/, '');
    
    await fs.mkdir(join(__dirname, '../../uploads'), { recursive: true });
    await fs.writeFile(imagePath, base64, 'base64');
    
    return imagePath;
  }
}
