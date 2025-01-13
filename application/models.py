from application import db, app

class Admin(db.Model):
    AdminID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    DOB = db.Column(db.Date)
    JoiningDate = db.Column(db.Date)

    admin_logs=db.relationship('AdminLogs',back_populates='admin',cascade='all, delete-orphan')

class Sponsor(db.Model):
    SponsorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    JoiningDate = db.Column(db.Date)
    Brand = db.Column(db.String(255))
    Industry = db.Column(db.String(255))
    Email = db.Column(db.String(255), nullable=False)
    PhoneNo = db.Column(db.String(255), nullable=False)
    BrandDescription = db.Column(db.String(255))
    Address = db.Column(db.String(255))
    Website = db.Column(db.String(255))
    Flagged = db.Column(db.Integer,nullable=False,default=0)
    ProfilePicLink=db.Column(db.String(255))

    campaigns = db.relationship('Campaign', back_populates='sponsor', cascade='all, delete-orphan')

class Influencer(db.Model):
    InfluencerID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    JoiningDate = db.Column(db.Date)
    Email = db.Column(db.String(255), nullable=False)
    PhoneNo = db.Column(db.String(255), nullable=False)
    Followers = db.Column(db.Integer)
    Bio = db.Column(db.String(255))
    Flagged = db.Column(db.Integer,nullable=False,default=0)
    ProfilePicLink=db.Column(db.String(255))
    
    campaigns = db.relationship('Campaign', back_populates='influencer', cascade='all, delete-orphan')
    ad_negotiations = db.relationship('AdNegotiation', back_populates='influencer', cascade='all, delete-orphan')

class Campaign(db.Model):
    CampaignID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text)
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)
    SponsorID = db.Column(db.Integer, db.ForeignKey('sponsor.SponsorID'), nullable=False)
    InfluencerID = db.Column(db.Integer, db.ForeignKey('influencer.InfluencerID'))
    Budget = db.Column(db.Float)
    Goal = db.Column(db.Text)
    Outreach = db.Column(db.Integer)
    Visibility = db.Column(db.Enum('Public', 'Private'))
    Flagged = db.Column(db.Integer,nullable=False,default=0)

    sponsor = db.relationship('Sponsor', back_populates='campaigns')
    influencer = db.relationship('Influencer', back_populates='campaigns')
    ad_requests = db.relationship('AdRequest', back_populates='campaign', cascade='all, delete-orphan')

class AdRequest(db.Model):
    __tablename__ = 'AdRequest'
    RequestID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False, unique=True)
    Description = db.Column(db.Text)
    Requirements = db.Column(db.Text)
    Payment = db.Column(db.Float)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID', ondelete='CASCADE'), nullable=False)
    Status = db.Column(db.String(10), default='Pending', nullable=False)

    campaign = db.relationship('Campaign', back_populates='ad_requests')
    ad_negotiations = db.relationship('AdNegotiation', back_populates='ad_request', cascade='all, delete-orphan')

    __table_args__=(
        db.CheckConstraint("Status IN ('Pending', 'Accepted','Closed')", name='check_status'),
    )

class AdNegotiation(db.Model):
    __tablename__ = 'AdNegotiation'

    RequestID = db.Column(db.Integer, db.ForeignKey('AdRequest.RequestID'), primary_key=True)
    InfluencerID = db.Column(db.Integer, db.ForeignKey('influencer.InfluencerID'), primary_key=True)
    Current_Negotiation = db.Column(db.Float, nullable=False)
    Sender = db.Column(db.String, nullable=False)
    Time = db.Column(db.DateTime, nullable=False)
    Status=db.Column(db.String,nullable=False)

    ad_request = db.relationship('AdRequest', back_populates='ad_negotiations')
    influencer = db.relationship('Influencer', back_populates='ad_negotiations')

    __table_args__ = (
        db.PrimaryKeyConstraint('RequestID', 'InfluencerID'),
        db.CheckConstraint("Sender IN ('Influencer', 'Sponsor')", name='check_sender'),
        db.CheckConstraint("Status IN ('Open','Accepted','Rejected','Closed')",name='check_status'),
    )

class AdminLogs(db.Model):
    __tablename__ = 'AdminLogs'

    LogID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    AdminID = db.Column(db.Integer, db.ForeignKey('admin.AdminID'), nullable=False)
    Action = db.Column(db.Text, nullable=False)
    Message = db.Column(db.Text)

    admin=db.relationship('Admin',back_populates='admin_logs')
