from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base_class import Base


class CRMCompany(Base):
    __tablename__ = "crm_companies"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(180), nullable=False, index=True)
    industry = Column(String(120), index=True)
    website = Column(String(200))
    phone = Column(String(40))
    email = Column(String(150), index=True)
    address = Column(Text)
    city = Column(String(100), index=True)
    state = Column(String(100))
    country = Column(String(100), default="India")
    employee_count = Column(Integer)
    annual_revenue = Column(Numeric(14, 2))
    account_type = Column(String(40), default="Prospect", index=True)
    status = Column(String(40), default="Active", index=True)
    tags_text = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMContact(Base):
    __tablename__ = "crm_contacts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="SET NULL"), nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    full_name = Column(String(220), nullable=False, index=True)
    email = Column(String(150), index=True)
    phone = Column(String(40))
    alternate_phone = Column(String(40))
    job_title = Column(String(120))
    department = Column(String(120))
    lifecycle_stage = Column(String(60), default="Lead", index=True)
    source = Column(String(80), index=True)
    date_of_birth = Column(Date)
    website = Column(String(200))
    linkedin_url = Column(String(300))
    twitter_url = Column(String(300))
    city = Column(String(100), index=True)
    state = Column(String(100))
    country = Column(String(100), default="India")
    address = Column(Text)
    status = Column(String(40), default="Active", index=True)
    customer_since = Column(Date)
    last_contacted_at = Column(DateTime(timezone=True))
    next_follow_up_at = Column(DateTime(timezone=True), index=True)
    tags_text = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMLead(Base):
    __tablename__ = "crm_leads"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_team_id = Column(Integer, nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    full_name = Column(String(220), nullable=False, index=True)
    email = Column(String(150), index=True)
    phone = Column(String(40), index=True)
    alternate_phone = Column(String(40))
    company_name = Column(String(180), index=True)
    job_title = Column(String(120))
    source = Column(String(80), default="Other", index=True)
    status = Column(String(40), default="New", index=True)
    rating = Column(String(20), default="Warm", index=True)
    industry = Column(String(120), index=True)
    website = Column(String(200))
    city = Column(String(100), index=True)
    state = Column(String(100))
    country = Column(String(100), default="India")
    address = Column(Text)
    estimated_value = Column(Numeric(12, 2))
    expected_close_date = Column(Date, index=True)
    last_contacted_at = Column(DateTime(timezone=True))
    next_follow_up_at = Column(DateTime(timezone=True), index=True)
    is_converted = Column(Boolean, default=False, index=True)
    converted_at = Column(DateTime(timezone=True))
    converted_contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True)
    converted_company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="SET NULL"), nullable=True)
    converted_deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="SET NULL"), nullable=True)
    tags_text = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMPipeline(Base):
    __tablename__ = "crm_pipelines"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    name = Column(String(160), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CRMPipelineStage(Base):
    __tablename__ = "crm_pipeline_stages"
    __table_args__ = (UniqueConstraint("pipeline_id", "name", name="uq_crm_pipeline_stage_name"),)

    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("crm_pipelines.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    probability = Column(Integer, default=0)
    position = Column(Integer, default=0)
    color = Column(String(30))
    is_won = Column(Boolean, default=False)
    is_lost = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CRMDeal(Base):
    __tablename__ = "crm_deals"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("crm_pipelines.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey("crm_pipeline_stages.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(180), nullable=False, index=True)
    description = Column(Text)
    amount = Column(Numeric(12, 2), default=0)
    currency = Column(String(10), default="INR")
    probability = Column(Integer, default=0)
    expected_revenue = Column(Numeric(12, 2))
    expected_close_date = Column(Date, index=True)
    actual_close_date = Column(Date)
    status = Column(String(30), default="Open", index=True)
    loss_reason = Column(Text)
    lead_source = Column(String(80), index=True)
    discount_amount = Column(Numeric(12, 2))
    position = Column(Integer, default=0)
    next_follow_up_at = Column(DateTime(timezone=True), index=True)
    last_activity_at = Column(DateTime(timezone=True))
    tags_text = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMProduct(Base):
    __tablename__ = "crm_products"
    __table_args__ = (UniqueConstraint("organization_id", "sku", name="uq_crm_product_org_sku"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    name = Column(String(180), nullable=False, index=True)
    sku = Column(String(80), index=True)
    category = Column(String(120), index=True)
    description = Column(Text)
    unit_price = Column(Numeric(12, 2), default=0)
    currency = Column(String(10), default="INR")
    tax_rate = Column(Numeric(5, 2))
    image_url = Column(String(500))
    status = Column(String(30), default="Active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMDealProduct(Base):
    __tablename__ = "crm_deal_products"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("crm_products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2))
    tax_rate = Column(Numeric(5, 2))
    total_amount = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CRMQuotation(Base):
    __tablename__ = "crm_quotations"
    __table_args__ = (UniqueConstraint("organization_id", "quote_number", name="uq_crm_quote_org_number"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="SET NULL"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    quote_number = Column(String(60), nullable=False, index=True)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="Draft", index=True)
    currency = Column(String(10), default="INR")
    subtotal = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2))
    tax_amount = Column(Numeric(12, 2))
    total_amount = Column(Numeric(12, 2), default=0)
    terms = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CRMQuotationItem(Base):
    __tablename__ = "crm_quotation_items"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("crm_quotations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("crm_products.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(180), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2))
    tax_rate = Column(Numeric(5, 2))
    total_amount = Column(Numeric(12, 2), default=0)


class CRMActivity(Base):
    __tablename__ = "crm_activities"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    activity_type = Column(String(40), nullable=False, index=True)
    subject = Column(String(180), nullable=False)
    description = Column(Text)
    status = Column(String(30), default="Pending", index=True)
    priority = Column(String(30), default="Medium", index=True)
    due_date = Column(DateTime(timezone=True), index=True)
    completed_at = Column(DateTime(timezone=True))
    outcome = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CRMTask(Base):
    __tablename__ = "crm_tasks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(220), nullable=False)
    description = Column(Text)
    status = Column(String(30), default="To Do", index=True)
    priority = Column(String(30), default="Medium", index=True)
    due_date = Column(DateTime(timezone=True), index=True)
    reminder_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMNote(Base):
    __tablename__ = "crm_notes"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    author_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    ticket_id = Column(Integer, ForeignKey("crm_tickets.id", ondelete="CASCADE"), nullable=True, index=True)
    body = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_internal = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMEmailLog(Base):
    __tablename__ = "crm_email_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    subject = Column(String(220), nullable=False)
    body = Column(Text)
    from_email = Column(String(150))
    to_email = Column(String(150), nullable=False, index=True)
    cc = Column(String(500))
    direction = Column(String(20), default="Outbound", index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CRMCallLog(Base):
    __tablename__ = "crm_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    direction = Column(String(20), nullable=False, index=True)
    phone_number = Column(String(40), nullable=False)
    duration_seconds = Column(Integer)
    outcome = Column(String(160))
    notes = Column(Text)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    call_time = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CRMMeeting(Base):
    __tablename__ = "crm_meetings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    title = Column(String(180), nullable=False)
    description = Column(Text)
    location = Column(String(240))
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    outcome = Column(Text)
    status = Column(String(30), default="Scheduled", index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CRMTicket(Base):
    __tablename__ = "crm_tickets"
    __table_args__ = (UniqueConstraint("organization_id", "ticket_number", name="uq_crm_ticket_org_number"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ticket_number = Column(String(60), nullable=False, index=True)
    subject = Column(String(220), nullable=False)
    description = Column(Text)
    priority = Column(String(30), default="Medium", index=True)
    status = Column(String(50), default="Open", index=True)
    category = Column(String(100), index=True)
    source = Column(String(40), default="Manual", index=True)
    due_date = Column(DateTime(timezone=True), index=True)
    resolved_at = Column(DateTime(timezone=True))
    satisfaction_rating = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMCampaign(Base):
    __tablename__ = "crm_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(180), nullable=False, index=True)
    campaign_type = Column(String(50), nullable=False, index=True)
    status = Column(String(30), default="Planned", index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    budget_amount = Column(Numeric(12, 2))
    actual_cost = Column(Numeric(12, 2))
    expected_revenue = Column(Numeric(12, 2))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMCampaignLead(Base):
    __tablename__ = "crm_campaign_leads"
    __table_args__ = (UniqueConstraint("campaign_id", "lead_id", name="uq_crm_campaign_lead"),)

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("crm_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CRMFileAsset(Base):
    __tablename__ = "crm_file_assets"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("crm_companies.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True, index=True)
    ticket_id = Column(Integer, ForeignKey("crm_tickets.id", ondelete="CASCADE"), nullable=True, index=True)
    file_name = Column(String(240), nullable=False)
    original_name = Column(String(240), nullable=False)
    mime_type = Column(String(120))
    size_bytes = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=False)
    visibility = Column(String(40), default="Internal", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class CRMTag(Base):
    __tablename__ = "crm_tags"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_crm_tag_org_name"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(30))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

