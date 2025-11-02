/**
 * API Adapter for Dify Components
 * Ensures compatibility between Dify UI components and RAG-ENTERPRISE backend
 */

export class ApiAdapter {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Adapt Dify API calls to RAG-ENTERPRISE endpoints
   */
  adaptEndpoint(difyEndpoint: string): string {
    // Map Dify endpoints to RAG-ENTERPRISE endpoints
    const mapping: Record<string, string> = {
      '/console/api/apps': '/apps',
      '/console/api/datasets': '/datasets',
      // Will be expanded as needed
    };

    return mapping[difyEndpoint] || difyEndpoint;
  }

  /**
   * Adapt request format
   */
  adaptRequest(data: any): any {
    // Transform if needed
    return data;
  }

  /**
   * Adapt response format
   */
  adaptResponse(response: any): any {
    // Transform if needed
    return response;
  }
}

export default new ApiAdapter();
