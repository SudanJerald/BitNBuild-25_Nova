# Sample Data Files for TaxWise

This folder contains sample financial data files that you can use to test the TaxWise application.

## 📁 Available Files

### 1. **bank_statement_sample.csv**
- **Type**: Bank Account Statement
- **Period**: January 2024 - April 2024 (4 months)
- **Transactions**: 48 entries
- **Contains**:
  - Monthly salary credits (₹85,000)
  - EMI payments (₹18,500/month)
  - House rent (₹25,000/month)
  - SIP investments (₹5,000/month)
  - Insurance premiums
  - Utility bills
  - Daily expenses (food, shopping, transport)
  - Interest credits

**Key Features for Tax Analysis**:
- Regular income (Salary)
- Home loan EMI (Section 24b deduction)
- SIP investments (Section 80C)
- Insurance premiums (Section 80C, 80D)
- PPF contribution (Section 80C)

### 2. **credit_card_statement_sample.csv**
- **Type**: Credit Card Statement
- **Period**: January 2024 - April 2024 (4 months)
- **Transactions**: 46 entries
- **Contains**:
  - Shopping expenses (Amazon, Flipkart, Myntra)
  - Food delivery (Swiggy, Zomato)
  - Transportation (Uber, Ola)
  - Entertainment (Netflix, BookMyShow, Spotify)
  - Fuel expenses
  - Healthcare expenses
  - Monthly payments

**Key Features for CIBIL Analysis**:
- Regular credit card usage
- Timely payment history
- Diverse spending categories
- Credit utilization patterns

### 3. **investment_transactions_sample.csv**
- **Type**: Investment Portfolio Transactions
- **Period**: January 2024 - April 2024 (4 months)
- **Transactions**: 22 entries
- **Contains**:
  - SIP (Systematic Investment Plan)
  - PPF contributions
  - ELSS tax-saver funds
  - NPS contributions
  - Dividend income
  - Fixed deposits
  - Stock investments
  - Gold bonds

**Key Features for Tax Optimization**:
- Section 80C investments (PPF, ELSS)
- Section 80CCD (NPS)
- Capital gains tracking
- Dividend income

## 🚀 How to Use

### Upload to TaxWise:

1. **Open the application** at http://localhost:3000
2. **Login** with your account
3. **Navigate to Upload Section**
4. **Choose file type**:
   - Bank Statement → `bank_statement_sample.csv`
   - Credit Card Statement → `credit_card_statement_sample.csv`
   - Investment Statement → `investment_transactions_sample.csv`
5. **Upload and wait** for processing
6. **View results** in:
   - Dashboard (spending overview)
   - Tax Optimizer (calculate tax liability)
   - CIBIL Advisor (credit score analysis)
   - Reports (downloadable summaries)

## 💡 Expected Results

### Tax Calculation:
- **Gross Income**: ₹3,40,000 (4 months × ₹85,000)
- **80C Deductions**: 
  - SIP: ₹20,000
  - PPF: ₹30,000
  - ELSS: ₹40,000
  - Insurance: ₹39,000
  - Total: ₹1,29,000
- **80D Deductions**: ₹8,500 (Health Insurance)
- **24b Deductions**: ₹74,000 (Home Loan Interest)
- **Recommended Regime**: Old (due to high deductions)

### CIBIL Score Factors:
- **Payment History**: Excellent (regular monthly payments)
- **Credit Utilization**: Good (payments made regularly)
- **Credit Mix**: Moderate (credit card + home loan)
- **Account Age**: Will depend on user profile
- **New Credit**: Stable (no new accounts)

### Spending Analysis:
- **Top Categories**:
  1. Housing (Rent + EMI): ₹1,74,000
  2. Investments: ₹1,29,000
  3. Shopping: ₹60,000+
  4. Food & Dining: ₹10,000+
  5. Transportation: ₹5,000+

## 📊 File Formats

All files are in **CSV format** which is:
- ✅ Easy to open in Excel/Google Sheets
- ✅ Simple to edit and customize
- ✅ Compatible with the TaxWise file processor
- ✅ Lightweight and fast to upload

## ✏️ Customization

You can modify these files to test different scenarios:

### Add More Transactions:
```csv
2024-05-01,New Transaction,1000,debit,Category
```

### Change Amounts:
- Increase salary to see higher tax impact
- Add more investments for 80C optimization
- Modify EMI amounts

### Test Edge Cases:
- Zero income months
- Large one-time expenses
- Multiple credit cards
- Different investment types

## 🎯 Use Cases

### For Developers:
- Test file upload functionality
- Validate transaction categorization
- Check tax calculation accuracy
- Verify CIBIL score algorithm
- Test dashboard visualizations

### For Demo/Presentation:
- Show realistic financial data
- Demonstrate tax optimization
- Explain CIBIL score factors
- Showcase AI-powered insights

### For Testing:
- Stress test with large datasets
- Validate edge cases
- Check error handling
- Performance testing

## 📝 Notes

- All amounts are in **Indian Rupees (₹)**
- Dates follow **YYYY-MM-DD** format
- Transaction types: `credit` (money in) or `debit` (money out)
- Categories are auto-detected by the AI but can be specified
- PAN and other personal details should be entered in user profile

## 🔒 Privacy

These are **synthetic sample files** created for testing purposes only. They do not contain any real personal or financial information.

---

**Happy Testing! 🚀**

For issues or questions, check the main project README or contact the development team.
