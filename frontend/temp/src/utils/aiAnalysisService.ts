// AI Analysis Service for TaxWise Platform
// Provides advanced financial transaction analysis and insights

export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  transaction_type: 'credit' | 'debit';
  category: string;
  subcategory?: string;
  is_recurring?: boolean;
  recurring_frequency?: string;
  tax_relevant?: boolean;
  tax_section?: string;
}

export interface FinancialPattern {
  patternType: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'irregular';
  confidence: number;
  transactions: Transaction[];
  averageAmount: number;
  totalAmount: number;
  description: string;
}

export interface AIInsight {
  type: 'positive' | 'warning' | 'info' | 'critical';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  actionable: boolean;
  recommendations?: string[];
}

export interface CIBILFactors {
  paymentHistory: number;
  creditUtilization: number;
  creditAge: number;
  creditMix: number;
  newCredit: number;
}

export interface TaxOptimizationSuggestion {
  section: string;
  currentUtilization: number;
  maxLimit: number;
  potentialSavings: number;
  recommendations: string[];
  priority: 'high' | 'medium' | 'low';
}

export class AIAnalysisService {
  private static readonly EXPENSE_CATEGORIES = {
    'Fixed': ['rent', 'emi', 'insurance', 'utilities'],
    'Variable': ['food', 'transportation', 'entertainment', 'shopping'],
    'Investment': ['sip', 'mutual fund', 'stocks', 'fd'],
    'Irregular': ['medical', 'travel', 'gifts', 'repair']
  };

  private static readonly TAX_SECTIONS = {
    '80C': { limit: 150000, description: 'Investments in ELSS, PPF, NSC, Life Insurance' },
    '80D': { limit: 25000, description: 'Health Insurance Premiums' },
    '80G': { limit: 100000, description: 'Donations to Charitable Organizations' },
    '24B': { limit: 200000, description: 'Home Loan Interest' },
    'HRA': { limit: null, description: 'House Rent Allowance' }
  };

  /**
   * Analyze spending patterns using AI-powered categorization
   */
  static analyzeSpendingPatterns(transactions: Transaction[]): FinancialPattern[] {
    const patterns: FinancialPattern[] = [];
    const groupedTransactions = this.groupTransactionsByPattern(transactions);

    Object.entries(groupedTransactions).forEach(([patternType, txns]) => {
      if (txns.length > 0) {
        const pattern = this.createFinancialPattern(patternType, txns);
        patterns.push(pattern);
      }
    });

    return patterns.sort((a, b) => b.totalAmount - a.totalAmount);
  }

  /**
   * Generate AI-powered financial insights
   */
  static generateAIInsights(transactions: Transaction[], patterns: FinancialPattern[]): AIInsight[] {
    const insights: AIInsight[] = [];
    
    // Calculate key metrics
    const totalIncome = this.calculateTotalIncome(transactions);
    const totalExpenses = this.calculateTotalExpenses(transactions);
    const savingsRate = totalIncome > 0 ? ((totalIncome - totalExpenses) / totalIncome) * 100 : 0;

    // Savings rate insights
    insights.push(...this.generateSavingsInsights(savingsRate, totalIncome, totalExpenses));
    
    // Pattern-based insights
    insights.push(...this.generatePatternInsights(patterns, totalIncome));
    
    // Tax optimization insights
    insights.push(...this.generateTaxInsights(transactions, totalIncome));
    
    // CIBIL improvement insights
    insights.push(...this.generateCIBILInsights(transactions, patterns));
    
    // Risk assessment insights
    insights.push(...this.generateRiskInsights(patterns, totalIncome));

    return insights.sort((a, b) => {
      const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  /**
   * Generate tax optimization suggestions
   */
  static generateTaxOptimization(transactions: Transaction[]): TaxOptimizationSuggestion[] {
    const suggestions: TaxOptimizationSuggestion[] = [];
    const taxRelevantTransactions = transactions.filter(t => t.tax_relevant);

    Object.entries(this.TAX_SECTIONS).forEach(([section, config]) => {
      const sectionTransactions = taxRelevantTransactions.filter(t => t.tax_section === section);
      const currentUtilization = sectionTransactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
      const maxLimit = config.limit || 0;
      const potentialSavings = this.calculateTaxSavings(Math.min(currentUtilization, maxLimit));

      if (maxLimit && currentUtilization < maxLimit) {
        const remaining = maxLimit - currentUtilization;
        suggestions.push({
          section,
          currentUtilization,
          maxLimit,
          potentialSavings: this.calculateTaxSavings(remaining),
          recommendations: this.getTaxRecommendations(section, remaining),
          priority: remaining > 50000 ? 'high' : remaining > 20000 ? 'medium' : 'low'
        });
      }
    });

    return suggestions;
  }

  /**
   * Analyze CIBIL score factors based on transaction patterns
   */
  static analyzeCIBILFactors(transactions: Transaction[], patterns: FinancialPattern[]): CIBILFactors {
    const emiPattern = patterns.find(p => p.patternType === 'EMI');
    const creditCardPattern = patterns.find(p => p.patternType === 'Credit Card');
    const totalIncome = this.calculateTotalIncome(transactions);

    return {
      paymentHistory: this.calculatePaymentHistoryScore(emiPattern, creditCardPattern),
      creditUtilization: this.calculateCreditUtilizationScore(creditCardPattern, totalIncome),
      creditAge: this.estimateCreditAge(transactions),
      creditMix: this.calculateCreditMixScore(patterns),
      newCredit: this.calculateNewCreditScore(transactions)
    };
  }

  /**
   * Predict future financial trends
   */
  static predictFinancialTrends(transactions: Transaction[], months: number = 6): any {
    const monthlyData = this.groupTransactionsByMonth(transactions);
    const trends = {
      income: this.calculateTrend(monthlyData, 'income'),
      expenses: this.calculateTrend(monthlyData, 'expenses'),
      savings: this.calculateTrend(monthlyData, 'savings'),
      investments: this.calculateTrend(monthlyData, 'investments')
    };

    return {
      trends,
      projections: this.generateProjections(trends, months),
      recommendations: this.generateTrendRecommendations(trends)
    };
  }

  // Private helper methods

  private static groupTransactionsByPattern(transactions: Transaction[]): { [key: string]: Transaction[] } {
    const groups: { [key: string]: Transaction[] } = {
      'Salary': [],
      'EMI': [],
      'SIP': [],
      'Insurance': [],
      'Rent': [],
      'Utilities': [],
      'Food': [],
      'Transportation': [],
      'Shopping': [],
      'Investment': [],
      'Others': []
    };

    transactions.forEach(txn => {
      const category = txn.category || 'Others';
      const key = this.mapCategoryToPattern(category);
      if (groups[key]) {
        groups[key].push(txn);
      } else {
        groups['Others'].push(txn);
      }
    });

    return groups;
  }

  private static mapCategoryToPattern(category: string): string {
    const categoryLower = category.toLowerCase();
    
    if (categoryLower.includes('salary') || categoryLower.includes('income')) return 'Salary';
    if (categoryLower.includes('emi') || categoryLower.includes('loan')) return 'EMI';
    if (categoryLower.includes('sip') || categoryLower.includes('mutual')) return 'SIP';
    if (categoryLower.includes('insurance')) return 'Insurance';
    if (categoryLower.includes('rent')) return 'Rent';
    if (['electricity', 'water', 'gas', 'mobile', 'internet'].some(u => categoryLower.includes(u))) return 'Utilities';
    if (categoryLower.includes('food') || categoryLower.includes('restaurant')) return 'Food';
    if (categoryLower.includes('transport') || categoryLower.includes('fuel')) return 'Transportation';
    if (categoryLower.includes('shop') || categoryLower.includes('mall')) return 'Shopping';
    if (categoryLower.includes('investment') || categoryLower.includes('equity')) return 'Investment';
    
    return 'Others';
  }

  private static createFinancialPattern(patternType: string, transactions: Transaction[]): FinancialPattern {
    const totalAmount = transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
    const averageAmount = totalAmount / transactions.length;
    const frequency = this.determineFrequency(transactions);
    const confidence = this.calculatePatternConfidence(transactions, frequency);

    return {
      patternType,
      frequency,
      confidence,
      transactions,
      averageAmount,
      totalAmount,
      description: this.generatePatternDescription(patternType, transactions.length, frequency, averageAmount)
    };
  }

  private static determineFrequency(transactions: Transaction[]): 'daily' | 'weekly' | 'monthly' | 'yearly' | 'irregular' {
    if (transactions.length < 2) return 'irregular';
    
    const dates = transactions.map(t => new Date(t.date)).sort();
    const intervals = [];
    
    for (let i = 1; i < dates.length; i++) {
      const daysDiff = (dates[i].getTime() - dates[i-1].getTime()) / (1000 * 60 * 60 * 24);
      intervals.push(daysDiff);
    }
    
    const avgInterval = intervals.reduce((sum, interval) => sum + interval, 0) / intervals.length;
    
    if (avgInterval <= 7) return 'weekly';
    if (avgInterval <= 35) return 'monthly';
    if (avgInterval <= 90) return 'irregular';
    if (avgInterval <= 400) return 'yearly';
    
    return 'irregular';
  }

  private static calculatePatternConfidence(transactions: Transaction[], frequency: string): number {
    if (transactions.length < 2) return 0.3;
    
    const amounts = transactions.map(t => Math.abs(t.amount));
    const avgAmount = amounts.reduce((sum, amt) => sum + amt, 0) / amounts.length;
    const variance = amounts.reduce((sum, amt) => sum + Math.pow(amt - avgAmount, 2), 0) / amounts.length;
    const stdDev = Math.sqrt(variance);
    const coefficientOfVariation = stdDev / avgAmount;
    
    // Lower coefficient of variation indicates more consistent pattern
    let confidence = Math.max(0, 1 - coefficientOfVariation);
    
    // Boost confidence for recurring patterns
    if (frequency === 'monthly' || frequency === 'weekly') {
      confidence *= 1.2;
    }
    
    return Math.min(1, confidence);
  }

  private static generatePatternDescription(patternType: string, count: number, frequency: string, averageAmount: number): string {
    const formattedAmount = `₹${averageAmount.toLocaleString()}`;
    return `${count} ${frequency} ${patternType.toLowerCase()} transactions averaging ${formattedAmount}`;
  }

  private static calculateTotalIncome(transactions: Transaction[]): number {
    return transactions
      .filter(t => t.transaction_type === 'credit')
      .reduce((sum, t) => sum + t.amount, 0);
  }

  private static calculateTotalExpenses(transactions: Transaction[]): number {
    return transactions
      .filter(t => t.transaction_type === 'debit')
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
  }

  private static generateSavingsInsights(savingsRate: number, totalIncome: number, totalExpenses: number): AIInsight[] {
    const insights: AIInsight[] = [];
    
    if (savingsRate > 30) {
      insights.push({
        type: 'positive',
        priority: 'medium',
        title: 'Excellent Savings Rate',
        description: `Your savings rate of ${savingsRate.toFixed(1)}% is outstanding and well above the recommended 20%.`,
        impact: 'Strong financial foundation for wealth building and emergency preparedness',
        actionable: true,
        recommendations: [
          'Consider increasing investments in equity mutual funds for higher returns',
          'Explore tax-saving investment options to optimize your tax liability',
          'Consider setting up additional SIPs for long-term wealth creation'
        ]
      });
    } else if (savingsRate > 20) {
      insights.push({
        type: 'positive',
        priority: 'low',
        title: 'Good Savings Discipline',
        description: `Your savings rate of ${savingsRate.toFixed(1)}% meets the recommended benchmark.`,
        impact: 'Adequate savings for financial goals and emergency funds',
        actionable: true,
        recommendations: [
          'Maintain current savings discipline',
          'Review and optimize recurring expenses for potential savings',
          'Consider increasing investment allocation gradually'
        ]
      });
    } else if (savingsRate > 10) {
      insights.push({
        type: 'warning',
        priority: 'medium',
        title: 'Moderate Savings Rate',
        description: `Your savings rate of ${savingsRate.toFixed(1)}% is below the ideal 20%. Consider optimizing expenses.`,
        impact: 'May limit achievement of long-term financial goals',
        actionable: true,
        recommendations: [
          'Analyze and reduce discretionary spending',
          'Look for ways to increase income through skill development',
          'Set up automatic savings to improve consistency'
        ]
      });
    } else {
      insights.push({
        type: 'critical',
        priority: 'high',
        title: 'Low Savings Rate Alert',
        description: `Your savings rate of ${savingsRate.toFixed(1)}% is concerning and needs immediate attention.`,
        impact: 'Significant risk to financial security and goal achievement',
        actionable: true,
        recommendations: [
          'Conduct detailed expense audit to identify cost-cutting opportunities',
          'Consider additional income sources',
          'Prioritize essential expenses and eliminate non-critical spending',
          'Seek professional financial counseling if needed'
        ]
      });
    }
    
    return insights;
  }

  private static generatePatternInsights(patterns: FinancialPattern[], totalIncome: number): AIInsight[] {
    const insights: AIInsight[] = [];
    
    // EMI analysis
    const emiPattern = patterns.find(p => p.patternType === 'EMI');
    if (emiPattern && totalIncome > 0) {
      const emiRatio = (emiPattern.totalAmount / totalIncome) * 100;
      if (emiRatio > 40) {
        insights.push({
          type: 'warning',
          priority: 'high',
          title: 'High EMI Burden',
          description: `Your EMI-to-income ratio of ${emiRatio.toFixed(1)}% exceeds the safe limit of 40%.`,
          impact: 'High EMI burden can negatively impact credit score and financial flexibility',
          actionable: true,
          recommendations: [
            'Consider loan consolidation or refinancing options',
            'Avoid taking new loans until EMI ratio improves',
            'Look for opportunities to prepay high-interest loans'
          ]
        });
      }
    }
    
    // Investment analysis
    const sipPattern = patterns.find(p => p.patternType === 'SIP');
    const investmentPattern = patterns.find(p => p.patternType === 'Investment');
    const totalInvestments = (sipPattern?.totalAmount || 0) + (investmentPattern?.totalAmount || 0);
    
    if (totalIncome > 0) {
      const investmentRate = (totalInvestments / totalIncome) * 100;
      if (investmentRate < 10) {
        insights.push({
          type: 'info',
          priority: 'medium',
          title: 'Low Investment Rate',
          description: `Your investment rate of ${investmentRate.toFixed(1)}% is below the recommended 15-20%.`,
          impact: 'Limited wealth creation and potential tax-saving opportunities',
          actionable: true,
          recommendations: [
            'Start systematic investment plans (SIPs) in equity mutual funds',
            'Utilize tax-saving investment options under Section 80C',
            'Consider diversifying investments across asset classes'
          ]
        });
      }
    }
    
    return insights;
  }

  private static generateTaxInsights(transactions: Transaction[], totalIncome: number): AIInsight[] {
    const insights: AIInsight[] = [];
    const taxOptimization = this.generateTaxOptimization(transactions);
    
    const highPriorityOptimizations = taxOptimization.filter(opt => opt.priority === 'high');
    if (highPriorityOptimizations.length > 0) {
      const totalPotentialSavings = highPriorityOptimizations.reduce((sum, opt) => sum + opt.potentialSavings, 0);
      
      insights.push({
        type: 'info',
        priority: 'high',
        title: 'Significant Tax Optimization Opportunity',
        description: `You could save up to ₹${totalPotentialSavings.toLocaleString()} in taxes by maximizing deductions.`,
        impact: 'Substantial tax savings that can be redirected to investments',
        actionable: true,
        recommendations: highPriorityOptimizations.flatMap(opt => opt.recommendations)
      });
    }
    
    return insights;
  }

  private static generateCIBILInsights(transactions: Transaction[], patterns: FinancialPattern[]): AIInsight[] {
    const insights: AIInsight[] = [];
    const cibilFactors = this.analyzeCIBILFactors(transactions, patterns);
    
    if (cibilFactors.creditUtilization > 30) {
      insights.push({
        type: 'warning',
        priority: 'high',
        title: 'High Credit Utilization',
        description: 'Your credit utilization appears high, which can negatively impact your CIBIL score.',
        impact: 'High credit utilization can lower your credit score by 50-100 points',
        actionable: true,
        recommendations: [
          'Pay down credit card balances to below 30% of limit',
          'Consider requesting credit limit increases',
          'Avoid closing old credit cards to maintain credit history'
        ]
      });
    }
    
    return insights;
  }

  private static generateRiskInsights(patterns: FinancialPattern[], totalIncome: number): AIInsight[] {
    const insights: AIInsight[] = [];
    
    // Check for irregular income patterns
    const salaryPattern = patterns.find(p => p.patternType === 'Salary');
    if (salaryPattern && salaryPattern.confidence < 0.7) {
      insights.push({
        type: 'warning',
        priority: 'medium',
        title: 'Irregular Income Pattern',
        description: 'Your income pattern shows irregularity, which may indicate financial instability.',
        impact: 'Irregular income can make financial planning challenging and affect loan eligibility',
        actionable: true,
        recommendations: [
          'Build a larger emergency fund to handle income volatility',
          'Consider diversifying income sources',
          'Focus on fixed expenses optimization'
        ]
      });
    }
    
    return insights;
  }

  private static calculateTaxSavings(amount: number): number {
    // Assuming 30% tax bracket for calculation
    return amount * 0.30;
  }

  private static getTaxRecommendations(section: string, remainingAmount: number): string[] {
    const recommendations: { [key: string]: string[] } = {
      '80C': [
        `Invest additional ₹${remainingAmount.toLocaleString()} in ELSS mutual funds`,
        'Consider increasing PPF contributions',
        'Look into NSC or tax-saving FDs'
      ],
      '80D': [
        `Increase health insurance coverage by ₹${remainingAmount.toLocaleString()}`,
        'Consider family floater health insurance plans',
        'Add critical illness or personal accident coverage'
      ],
      '80G': [
        `Donate ₹${remainingAmount.toLocaleString()} to eligible charitable organizations`,
        'Consider donations to PM-CARES or other government funds',
        'Set up systematic donation plans'
      ]
    };
    
    return recommendations[section] || [];
  }

  // Additional private methods for CIBIL analysis
  private static calculatePaymentHistoryScore(emiPattern?: FinancialPattern, creditCardPattern?: FinancialPattern): number {
    // Simplified calculation - in real implementation, would analyze payment delays
    if (!emiPattern && !creditCardPattern) return 50; // No credit history
    
    const emiConsistency = emiPattern ? emiPattern.confidence * 100 : 100;
    const creditConsistency = creditCardPattern ? creditCardPattern.confidence * 100 : 100;
    
    return Math.min(100, (emiConsistency + creditConsistency) / 2);
  }

  private static calculateCreditUtilizationScore(creditCardPattern?: FinancialPattern, totalIncome?: number): number {
    if (!creditCardPattern || !totalIncome) return 85; // Assume good utilization if no data
    
    const avgMonthlySpend = creditCardPattern.averageAmount;
    const estimatedLimit = totalIncome * 0.1; // Assume 10% of income as limit
    const utilizationRatio = avgMonthlySpend / estimatedLimit;
    
    if (utilizationRatio < 0.1) return 100;
    if (utilizationRatio < 0.3) return 85;
    if (utilizationRatio < 0.5) return 70;
    if (utilizationRatio < 0.7) return 50;
    return 30;
  }

  private static estimateCreditAge(transactions: Transaction[]): number {
    const creditTransactions = transactions.filter(t => 
      t.category?.toLowerCase().includes('credit') || 
      t.category?.toLowerCase().includes('loan')
    );
    
    if (creditTransactions.length === 0) return 50;
    
    const oldestTransaction = new Date(Math.min(...creditTransactions.map(t => new Date(t.date).getTime())));
    const ageInMonths = (Date.now() - oldestTransaction.getTime()) / (1000 * 60 * 60 * 24 * 30);
    
    return Math.min(100, (ageInMonths / 60) * 100); // 5 years = 100 score
  }

  private static calculateCreditMixScore(patterns: FinancialPattern[]): number {
    const creditTypes = ['EMI', 'Credit Card', 'Investment'].filter(type => 
      patterns.some(p => p.patternType === type)
    );
    
    return Math.min(100, (creditTypes.length / 3) * 100);
  }

  private static calculateNewCreditScore(transactions: Transaction[]): number {
    // Check for new credit inquiries in last 6 months
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    
    const recentCreditTransactions = transactions.filter(t => 
      new Date(t.date) > sixMonthsAgo && 
      (t.category?.toLowerCase().includes('loan') || t.category?.toLowerCase().includes('credit'))
    );
    
    if (recentCreditTransactions.length === 0) return 100;
    if (recentCreditTransactions.length <= 2) return 85;
    if (recentCreditTransactions.length <= 4) return 70;
    return 50;
  }

  private static groupTransactionsByMonth(transactions: Transaction[]): any {
    // Implementation for trend analysis
    return {};
  }

  private static calculateTrend(monthlyData: any, type: string): any {
    // Implementation for trend calculation
    return { direction: 'stable', magnitude: 0 };
  }

  private static generateProjections(trends: any, months: number): any {
    // Implementation for financial projections
    return {};
  }

  private static generateTrendRecommendations(trends: any): string[] {
    // Implementation for trend-based recommendations
    return [];
  }
}