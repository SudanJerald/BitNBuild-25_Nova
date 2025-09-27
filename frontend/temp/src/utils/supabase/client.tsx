import { createClient } from '@supabase/supabase-js'
import { projectId, publicAnonKey, supabaseUrl } from './info'

// Create a single supabase client for interacting with your database
export const supabase = createClient(
  supabaseUrl,
  publicAnonKey
)

// API helper functions - Connect to your Flask backend
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:5000'

// API Configuration
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  getAuthHeaders: (accessToken?: string) => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken || publicAnonKey}`
  })
}

// Simplified API helper class - Non-auth methods only
export class DatabaseAPI {

  // Profile methods - Updated for Flask backend
  static async getProfile(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/auth/profile/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch profile')
    }
    
    return response.json()
  }

  static async updateProfile(userId: string, profileData: any, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/auth/profile/${userId}`, {
      method: 'PUT',
      headers: API_CONFIG.getAuthHeaders(accessToken),
      body: JSON.stringify(profileData)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to update profile')
    }
    
    return response.json()
  }

  // Dashboard methods - New for TaxWise backend
  static async getDashboardOverview(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/dashboard/overview/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch dashboard data')
    }
    
    return response.json()
  }

  static async getChartData(userId: string, chartType: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/dashboard/charts/${userId}?type=${chartType}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch chart data')
    }
    
    return response.json()
  }

  // Health check method
  static async healthCheck() {
    const response = await fetch(`${API_CONFIG.BASE_URL}/health`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders()
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Backend health check failed')
    }
    
    return response.json()
  }

  // File methods - Updated for TaxWise backend
  static async uploadFile(userId: string, file: File, fileType: string, accessToken: string) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId)
    formData.append('file_type', fileType) // 'bank_statement', 'credit_card', 'csv'

    const response = await fetch(`${API_CONFIG.BASE_URL}/api/data/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to upload file')
    }
    
    return response.json()
  }

  static async getUserTransactions(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/data/transactions/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch transactions')
    }
    
    return response.json()
  }

  static async getFinancialData(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/data/financial/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch financial data')
    }
    
    return response.json()
  }

  // Tax calculation methods
  static async calculateTax(userId: string, taxData: any, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/tax/calculate/${userId}`, {
      method: 'POST',
      headers: API_CONFIG.getAuthHeaders(accessToken),
      body: JSON.stringify(taxData)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to calculate tax')
    }
    
    return response.json()
  }

  static async getTaxOptimization(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/tax/optimization/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to get tax optimization')
    }
    
    return response.json()
  }

  // CIBIL methods
  static async getCibilScore(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/cibil/score/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch CIBIL score')
    }
    
    return response.json()
  }

  static async getCibilRecommendations(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/cibil/recommendations/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch CIBIL recommendations')
    }
    
    return response.json()
  }

  // Analytics and Insights methods  
  static async getSpendingAnalysis(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/dashboard/charts/${userId}?type=spending`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch spending analysis')
    }
    
    return response.json()
  }

  static async getIncomeAnalysis(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/dashboard/charts/${userId}?type=income`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch income analysis')
    }
    
    return response.json()
  }

  static async getTaxHistory(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/tax/history/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch tax history')
    }
    
    return response.json()
  }

  // Additional methods for ProfileSection and other components
  static async getAccounts(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/accounts/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch accounts')
    }
    
    return response.json()
  }

  static async connectAccount(userId: string, accountData: any, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/accounts/connect`, {
      method: 'POST',
      headers: API_CONFIG.getAuthHeaders(accessToken),
      body: JSON.stringify({ user_id: userId, ...accountData })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to connect account')
    }
    
    return response.json()
  }

  static async disconnectAccount(userId: string, accountId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/accounts/${accountId}`, {
      method: 'DELETE',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to disconnect account')
    }
    
    return response.json()
  }

  static async getNotificationSettings(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/notifications/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch notification settings')
    }
    
    return response.json()
  }

  static async updateNotificationSettings(userId: string, settings: any, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/notifications/${userId}`, {
      method: 'PUT',
      headers: API_CONFIG.getAuthHeaders(accessToken),
      body: JSON.stringify(settings)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to update notification settings')
    }
    
    return response.json()
  }

  static async getReports(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/reports/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch reports')
    }
    
    return response.json()
  }

  static async saveReport(userId: string, reportData: any, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/reports`, {
      method: 'POST',
      headers: API_CONFIG.getAuthHeaders(accessToken),
      body: JSON.stringify({ user_id: userId, ...reportData })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to save report')
    }
    
    return response.json()
  }

  static async getUserFiles(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/files/${userId}`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch user files')
    }
    
    return response.json()
  }
}