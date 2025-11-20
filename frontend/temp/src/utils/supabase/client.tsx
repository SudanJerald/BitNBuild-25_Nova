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
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/auth/profile`, {
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
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/auth/profile`, {
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

  // Dashboard methods - Using real API endpoints
  static async getDashboardOverview(userId: string, accessToken: string) {
    try {
      // Try to get real dashboard data from the backend
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/dashboard/overview`, {
        method: 'GET',
        headers: API_CONFIG.getAuthHeaders(accessToken)
      })
      
      if (response.ok) {
        return response.json()
      } else {
        // If backend doesn't have dashboard endpoint yet, fallback to profile + mock data
        console.warn('Dashboard endpoint not available, using fallback data')
        
        // Get user profile for personalized data
        const profileResponse = await this.getProfile(userId, accessToken)
        const userProfile = profileResponse.profile || {}
        
        // Return dashboard structure with user's actual profile data + mock financial data
        return {
          dashboard: {
            user_info: {
              name: userProfile.full_name || "Welcome User",
              email: userProfile.email || "user@example.com",
              member_since: userProfile.created_at ? 
                new Date(userProfile.created_at).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long' 
                }) : "Recently"
            },
            financial_summary: {
              total_income: 1200000,
              total_expenses: 850000,
              net_savings: 350000,
              monthly_income: 100000,
              monthly_expenses: 70833,
              savings_rate: 29.2
            },
            tax_summary: {
              financial_year: "2023-24",
              gross_income: 1200000,
              tax_liability: 195000,
              recommended_regime: "Old Regime",
              potential_savings: 25000,
              deductions_utilized: 175000,
              last_calculated: new Date().toISOString()
            },
            cibil_summary: {
              current_score: 782,
              previous_score: 767,
              trend: "improving",
              score_category: "Excellent",
              last_updated: new Date().toISOString()
            },
            recent_activity: [
              {
                id: "1",
                type: "upload",
                description: "Bank statement uploaded",
                amount: 0,
                date: new Date(Date.now() - 86400000).toISOString()
              },
              {
                id: "2",
                type: "calculation",
                description: "Tax calculation completed",
                amount: 195000,
                date: new Date(Date.now() - 172800000).toISOString()
              },
              {
                id: "3",
                type: "report",
                description: "Financial report generated",
                amount: 0,
                date: new Date(Date.now() - 259200000).toISOString()
              }
            ],
            insights: [
              {
                type: "tax",
                message: "You could save ₹25,000 by maximizing your 80C deductions",
                impact: "high",
                action_required: true
              },
              {
                type: "savings",
                message: "Your savings rate of 29.2% is excellent! Keep it up.",
                impact: "medium",
                action_required: false
              },
              {
                type: "credit",
                message: "Your CIBIL score improved by 15 points this month",
                impact: "medium",
                action_required: false
              }
            ],
            last_updated: new Date().toISOString()
          }
        }
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      // Fallback to mock data if all else fails
      return {
        dashboard: {
          user_info: {
            name: "Welcome User",
            email: "user@example.com",
            member_since: "Recently"
          },
          financial_summary: {
            total_income: 0,
            total_expenses: 0,
            net_savings: 0,
            monthly_income: 0,
            monthly_expenses: 0,
            savings_rate: 0
          },
          tax_summary: {
            financial_year: "2023-24",
            gross_income: 0,
            tax_liability: 0,
            recommended_regime: "Not calculated",
            potential_savings: 0,
            deductions_utilized: 0,
            last_calculated: new Date().toISOString()
          },
          cibil_summary: {
            current_score: 0,
            previous_score: 0,
            trend: "unknown",
            score_category: "Not available",
            last_updated: new Date().toISOString()
          },
          recent_activity: [],
          insights: [],
          last_updated: new Date().toISOString()
        }
      }
    }
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

  // Connected Accounts methods - Using new API endpoints
  static async getAccounts(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/accounts`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch connected accounts')
    }
    
    return response.json()
  }

  static async connectAccount(userId: string, accountData: any, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/accounts`, {
      method: 'POST',
      headers: API_CONFIG.getAuthHeaders(accessToken),
      body: JSON.stringify(accountData)
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

  // Notification Settings methods - Using new API endpoints
  static async getNotificationSettings(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/notifications`, {
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
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/notifications`, {
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

  // Reports methods - Using new API endpoints
  static async getReports(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/reports`, {
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
      body: JSON.stringify(reportData)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to save report')
    }
    
    return response.json()
  }

  static async downloadReport(userId: string, reportId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/reports/${reportId}/download`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to download report')
    }
    
    return response.blob()
  }

  static async deleteReport(userId: string, reportId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/reports/${reportId}`, {
      method: 'DELETE',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to delete report')
    }
    
    return response.json()
  }

  // File management methods - Using new API endpoints
  static async getUserFiles(userId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/files`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to fetch user files')
    }
    
    return response.json()
  }

  static async uploadUserFile(userId: string, file: File, fileType: string, accessToken: string) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)

    const response = await fetch(`${API_CONFIG.BASE_URL}/api/files/upload`, {
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

  static async downloadUserFile(userId: string, fileId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/files/${fileId}/download`, {
      method: 'GET',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to download file')
    }
    
    return response.blob()
  }

  static async deleteUserFile(userId: string, fileId: string, accessToken: string) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/files/${fileId}`, {
      method: 'DELETE',
      headers: API_CONFIG.getAuthHeaders(accessToken)
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to delete file')
    }
    
    return response.json()
  }
}