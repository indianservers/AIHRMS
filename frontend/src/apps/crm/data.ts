export type CRMLead = {
  id: number;
  name: string;
  company: string;
  email: string;
  phone: string;
  source: string;
  status: string;
  rating: "Cold" | "Warm" | "Hot";
  owner: string;
  value: number;
  nextFollowUp: string;
  lastContacted: string;
  industry: string;
};

export type CRMDeal = {
  id: number;
  name: string;
  company: string;
  contact: string;
  owner: string;
  stage: string;
  amount: number;
  probability: number;
  closeDate: string;
  nextStep: string;
  products: string[];
};

export type CRMRecord = Record<string, string | number>;

export const pipelineStages = [
  "Prospecting",
  "Qualification",
  "Needs Analysis",
  "Proposal Sent",
  "Negotiation",
  "Contract Sent",
  "Won",
  "Lost",
];

export const crmLeads: CRMLead[] = [
  { id: 1, name: "Rahul Mehta", company: "Apex Digital Solutions", email: "rahul@apexdigital.in", phone: "+91 98765 11001", source: "Website", status: "Qualified", rating: "Hot", owner: "Ananya Rao", value: 850000, nextFollowUp: "2026-05-09", lastContacted: "2026-05-06", industry: "Software Services" },
  { id: 2, name: "Priya Nair", company: "GreenField Realty", email: "priya@greenfield.example", phone: "+91 98765 11002", source: "Referral", status: "Contacted", rating: "Warm", owner: "Karan Shah", value: 420000, nextFollowUp: "2026-05-10", lastContacted: "2026-05-04", industry: "Real Estate" },
  { id: 3, name: "Vikram Sethi", company: "BrightPath Academy", email: "vikram@brightpath.example", phone: "+91 98765 11003", source: "Event", status: "New", rating: "Warm", owner: "Meera Iyer", value: 320000, nextFollowUp: "2026-05-12", lastContacted: "2026-05-02", industry: "Education" },
  { id: 4, name: "Fatima Khan", company: "HealthBridge Clinics", email: "fatima@healthbridge.example", phone: "+91 98765 11004", source: "Phone Call", status: "Nurturing", rating: "Cold", owner: "Ananya Rao", value: 250000, nextFollowUp: "2026-05-16", lastContacted: "2026-04-30", industry: "Healthcare" },
  { id: 5, name: "Arjun Reddy", company: "Nova Manufacturing", email: "arjun@novamfg.example", phone: "+91 98765 11005", source: "Partner", status: "Qualified", rating: "Hot", owner: "Karan Shah", value: 1200000, nextFollowUp: "2026-05-08", lastContacted: "2026-05-05", industry: "Manufacturing" },
  { id: 6, name: "Neha Kapoor", company: "UrbanCart Retail", email: "neha@urbancart.example", phone: "+91 98765 11006", source: "Email Campaign", status: "Contacted", rating: "Warm", owner: "Rahul Singh", value: 510000, nextFollowUp: "2026-05-11", lastContacted: "2026-05-03", industry: "Retail" },
  { id: 7, name: "Dev Malhotra", company: "FinEdge Advisors", email: "dev@finedge.example", phone: "+91 98765 11007", source: "Marketplace", status: "Converted", rating: "Hot", owner: "Meera Iyer", value: 960000, nextFollowUp: "2026-05-14", lastContacted: "2026-05-06", industry: "Financial Services" },
  { id: 8, name: "Sara Thomas", company: "StratEdge Consulting", email: "sara@stratedge.example", phone: "+91 98765 11008", source: "Social Media", status: "New", rating: "Cold", owner: "Rahul Singh", value: 280000, nextFollowUp: "2026-05-15", lastContacted: "2026-05-01", industry: "Consulting" },
];

export const crmDeals: CRMDeal[] = [
  { id: 1, name: "Website Development Contract", company: "Apex Digital Solutions", contact: "Rahul Mehta", owner: "Ananya Rao", stage: "Prospecting", amount: 450000, probability: 10, closeDate: "2026-05-28", nextStep: "Confirm discovery scope", products: ["Implementation Package"] },
  { id: 2, name: "ERP Implementation Deal", company: "Nova Manufacturing", contact: "Arjun Reddy", owner: "Karan Shah", stage: "Qualification", amount: 1800000, probability: 25, closeDate: "2026-06-18", nextStep: "Map plant rollout timeline", products: ["Enterprise Suite", "Data Migration"] },
  { id: 3, name: "Annual Software License", company: "FinEdge Advisors", contact: "Dev Malhotra", owner: "Meera Iyer", stage: "Needs Analysis", amount: 960000, probability: 40, closeDate: "2026-06-02", nextStep: "Security review", products: ["CRM Growth"] },
  { id: 4, name: "Digital Marketing Retainer", company: "UrbanCart Retail", contact: "Neha Kapoor", owner: "Ananya Rao", stage: "Proposal Sent", amount: 720000, probability: 55, closeDate: "2026-05-30", nextStep: "Revise campaign ROI model", products: ["Marketing Automation"] },
  { id: 5, name: "Real Estate CRM Setup", company: "GreenField Realty", contact: "Priya Nair", owner: "Karan Shah", stage: "Negotiation", amount: 650000, probability: 70, closeDate: "2026-05-24", nextStep: "Discount approval", products: ["CRM Starter", "Implementation Package"] },
  { id: 6, name: "Support Contract Renewal", company: "HealthBridge Clinics", contact: "Fatima Khan", owner: "Meera Iyer", stage: "Contract Sent", amount: 380000, probability: 85, closeDate: "2026-05-20", nextStep: "Legal signoff", products: ["Support Retainer"] },
  { id: 7, name: "Training Program Partnership", company: "BrightPath Academy", contact: "Vikram Sethi", owner: "Rahul Singh", stage: "Won", amount: 540000, probability: 100, closeDate: "2026-05-12", nextStep: "Create onboarding task", products: ["Training Pack"] },
  { id: 8, name: "Cloud Migration Project", company: "StratEdge Consulting", contact: "Sara Thomas", owner: "Rahul Singh", stage: "Lost", amount: 780000, probability: 0, closeDate: "2026-05-07", nextStep: "Record loss reason", products: ["Data Migration"] },
];

export const crmCompanies: CRMRecord[] = [
  { name: "Apex Digital Solutions", industry: "Software Services", type: "Prospect", status: "Active", revenue: 24000000, owner: "Ananya Rao" },
  { name: "GreenField Realty", industry: "Real Estate", type: "Customer", status: "Active", revenue: 18000000, owner: "Karan Shah" },
  { name: "BrightPath Academy", industry: "Education", type: "Customer", status: "Active", revenue: 9000000, owner: "Rahul Singh" },
  { name: "Nova Manufacturing", industry: "Manufacturing", type: "Customer", status: "Active", revenue: 65000000, owner: "Karan Shah" },
  { name: "HealthBridge Clinics", industry: "Healthcare", type: "Customer", status: "Active", revenue: 31000000, owner: "Meera Iyer" },
  { name: "UrbanCart Retail", industry: "Retail", type: "Prospect", status: "Active", revenue: 46000000, owner: "Ananya Rao" },
];

export const crmActivities: CRMRecord[] = [
  { subject: "Discovery call with Apex", type: "Call", owner: "Ananya Rao", due: "2026-05-08", status: "Pending", priority: "High" },
  { subject: "Proposal follow-up", type: "Email", owner: "Karan Shah", due: "2026-05-09", status: "Pending", priority: "Medium" },
  { subject: "Product demo", type: "Meeting", owner: "Meera Iyer", due: "2026-05-11", status: "Scheduled", priority: "High" },
  { subject: "Quote revision", type: "Task", owner: "Ananya Rao", due: "2026-05-07", status: "Overdue", priority: "Urgent" },
  { subject: "Contract review", type: "Meeting", owner: "Rahul Singh", due: "2026-05-13", status: "Pending", priority: "Medium" },
];

export const crmProducts: CRMRecord[] = [
  { name: "CRM Starter", sku: "CRM-ST", category: "Software", price: 49999, status: "Active" },
  { name: "CRM Growth", sku: "CRM-GR", category: "Software", price: 149999, status: "Active" },
  { name: "Enterprise Suite", sku: "ENT-SUITE", category: "Software", price: 425000, status: "Active" },
  { name: "Implementation Package", sku: "IMP-PRO", category: "Services", price: 175000, status: "Active" },
  { name: "Support Retainer", sku: "SUP-12", category: "Services", price: 300000, status: "Active" },
  { name: "Data Migration", sku: "DATA-MIG", category: "Services", price: 90000, status: "Active" },
];

export const crmTickets: CRMRecord[] = [
  { number: "TCK-1042", subject: "Email sync not updating", priority: "High", status: "Open", company: "Apex Digital Solutions", owner: "Support Desk" },
  { number: "TCK-1043", subject: "Need quotation PDF change", priority: "Medium", status: "Waiting for Customer", company: "GreenField Realty", owner: "Support Desk" },
  { number: "TCK-1044", subject: "User access request", priority: "Low", status: "Resolved", company: "BrightPath Academy", owner: "Support Desk" },
  { number: "TCK-1045", subject: "SLA report mismatch", priority: "Critical", status: "In Progress", company: "Nova Manufacturing", owner: "Support Desk" },
];

export const crmCampaigns: CRMRecord[] = [
  { campaign: "Website Lead Magnet", type: "Email", status: "Active", budget: 180000, leads: 42, converted: 8, roi: "220%" },
  { campaign: "Real Estate Webinar", type: "Webinar", status: "Planned", budget: 90000, leads: 16, converted: 2, roi: "80%" },
  { campaign: "Healthcare Outreach", type: "Cold Calling", status: "Active", budget: 120000, leads: 25, converted: 4, roi: "140%" },
  { campaign: "Retail Growth Ads", type: "Advertisement", status: "Paused", budget: 210000, leads: 31, converted: 5, roi: "95%" },
];

export const crmQuotations: CRMRecord[] = [
  { quote: "QT-1001", deal: "ERP Implementation Deal", company: "Nova Manufacturing", status: "Sent", issueDate: "2026-05-02", expiryDate: "2026-05-16", total: 1800000 },
  { quote: "QT-1002", deal: "Real Estate CRM Setup", company: "GreenField Realty", status: "Draft", issueDate: "2026-05-05", expiryDate: "2026-05-19", total: 650000 },
  { quote: "QT-1003", deal: "Support Contract Renewal", company: "HealthBridge Clinics", status: "Accepted", issueDate: "2026-04-28", expiryDate: "2026-05-12", total: 380000 },
  { quote: "QT-1004", deal: "Digital Marketing Retainer", company: "UrbanCart Retail", status: "Sent", issueDate: "2026-05-06", expiryDate: "2026-05-20", total: 720000 },
];

export const crmFiles: CRMRecord[] = [
  { file: "apex-discovery-notes.pdf", linkedTo: "Apex Digital Solutions", type: "PDF", visibility: "Team", status: "Ready" },
  { file: "nova-erp-proposal.xlsx", linkedTo: "ERP Implementation Deal", type: "Spreadsheet", visibility: "Private", status: "Ready" },
  { file: "greenfield-quote-v2.pdf", linkedTo: "QT-1002", type: "PDF", visibility: "Customer Visible", status: "Ready" },
  { file: "healthbridge-sla.docx", linkedTo: "TCK-1045", type: "Document", visibility: "Team", status: "Review" },
];

export const crmAutomationRules: CRMRecord[] = [
  { rule: "Assign website leads", trigger: "Lead created", condition: "Source = Website", action: "Round-robin owner", status: "Active" },
  { rule: "Qualified lead follow-up", trigger: "Status changes", condition: "Status = Qualified", action: "Create task", status: "Active" },
  { rule: "Quote expiry reminder", trigger: "Daily schedule", condition: "Expiry in 1 day", action: "Notify owner", status: "Active" },
  { rule: "Critical ticket escalation", trigger: "Ticket created", condition: "Priority = Critical", action: "Notify manager", status: "Active" },
];

export const crmSettingsRows: CRMRecord[] = [
  { setting: "Lead sources", area: "Leads", owner: "CRM Admin", status: "Ready" },
  { setting: "Pipeline stages", area: "Deals", owner: "Sales Ops", status: "Ready" },
  { setting: "Loss reasons", area: "Deals", owner: "Sales Manager", status: "Ready" },
  { setting: "Ticket categories", area: "Support", owner: "Support Lead", status: "Ready" },
  { setting: "Notification preferences", area: "Platform", owner: "CRM Admin", status: "Ready" },
];

export const crmAdminRows: CRMRecord[] = [
  { adminArea: "Users", permission: "Manage CRM users", count: 14, status: "Ready" },
  { adminArea: "Roles", permission: "Configure CRM permissions", count: 7, status: "Ready" },
  { adminArea: "Teams", permission: "Sales and support teams", count: 5, status: "Ready" },
  { adminArea: "Audit logs", permission: "Review changes", count: 128, status: "Ready" },
  { adminArea: "Templates", permission: "Email and quote templates", count: 12, status: "Ready" },
];
