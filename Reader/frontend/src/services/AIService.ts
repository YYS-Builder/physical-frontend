import axios from 'axios';
import { api } from './api';

export interface DocumentSummary {
  summary: string;
  length: number;
}

export interface DocumentKeywords {
  keywords: string[];
  count: number;
}

export interface DocumentSentiment {
  positive: number;
  negative: number;
  neutral: number;
}

export interface DocumentCategory {
  category: string;
  confidence: number;
}

export interface DocumentEntity {
  text: string;
  type: string;
  start: number;
  end: number;
}

export class AIService {
  private static instance: AIService;

  private constructor() {}

  public static getInstance(): AIService {
    if (!AIService.instance) {
      AIService.instance = new AIService();
    }
    return AIService.instance;
  }

  async summarizeDocument(documentId: string, maxLength: number = 500): Promise<DocumentSummary> {
    try {
      const response = await api.post(`/documents/${documentId}/summarize`, { maxLength });
      return {
        summary: response.data,
        length: response.data.length
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to summarize document');
      }
      throw error;
    }
  }

  async extractKeywords(documentId: string, numKeywords: number = 10): Promise<DocumentKeywords> {
    try {
      const response = await api.post(`/documents/${documentId}/keywords`, { numKeywords });
      return {
        keywords: response.data,
        count: response.data.length
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to extract keywords');
      }
      throw error;
    }
  }

  async analyzeSentiment(documentId: string): Promise<DocumentSentiment> {
    try {
      const response = await api.post(`/documents/${documentId}/sentiment`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to analyze sentiment');
      }
      throw error;
    }
  }

  async classifyDocument(documentId: string): Promise<DocumentCategory[]> {
    try {
      const response = await api.post(`/documents/${documentId}/classify`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to classify document');
      }
      throw error;
    }
  }

  async getEntities(documentId: string): Promise<DocumentEntity[]> {
    try {
      const response = await api.post(`/documents/${documentId}/entities`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to extract entities');
      }
      throw error;
    }
  }
}

export const aiService = AIService.getInstance(); 