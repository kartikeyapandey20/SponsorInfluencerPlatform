from flask import Flask, render_template,redirect,url_for,flash,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from application.models import*
from application.home_controllers import login_required
from application import engine
import os
from application.charts_controllers import num_inf,num_spon,num_camp

@app.route('/admin/home/<int:admin_ID>',methods=["GET"])
@login_required(role='admin')
def admin_home(admin_ID):
    admin=db.session.query(Admin).filter(Admin.AdminID==admin_ID).one()
    inf_link='num_inf.png'
    spon_link='num_spon.png'
    camp_link='num_camp.png'
    num_inf(inf_link)
    num_spon(spon_link)
    num_camp(camp_link)
    return render_template("Admin_home.html",admin=admin)

@app.route('/admin/profile/<int:admin_ID>',methods=['GET'])
@login_required(role='admin')
def admin_profile(admin_ID):
    admin=db.session.query(Admin).filter(Admin.AdminID==admin_ID).one()
    return render_template('Admin_profile.html',admin=admin)

@app.route('/admin/profile_picture/edit/<int:admin_ID>',methods=['GET','POST'])
@login_required(role='admin')
def admin_profile_edit(admin_ID):
    admin=db.session.query(Admin).filter(Admin.AdminID==admin_ID).one()
    if request.method=='GET':
        return render_template('Admin_profile_edit.html',admin=admin)
    
@app.route('/admin/campaigns/<int:admin_ID>',methods=['GET'])
@login_required(role='admin')
def admin_campaigns(admin_ID):
    from datetime import datetime
    today=datetime.today()
    active_campaigns=(db.session.query(Campaign,Influencer,Sponsor)
                      .filter(Campaign.EndDate>=today)
                      .join(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
                      .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
                      .order_by(Campaign.CampaignID)
                      .all())
    completed_campaigns=(db.session.query(Campaign,Influencer,Sponsor)
                      .filter(Campaign.EndDate<today)
                      .join(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
                      .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
                      .order_by(Campaign.CampaignID)
                      .all())    
    return render_template('Admin_campaigns.html',active=active_campaigns,completed=completed_campaigns,admin_ID=admin_ID)

@app.route('/admin/campaign/campaign_details/<int:admin_ID>/<campaign_ID>',methods=['GET'])
@login_required(role='admin')
def admin_campaign_details(admin_ID,campaign_ID):
    (camp,inf,spon)=(db.session.query(Campaign,Influencer,Sponsor)
                      .filter(Campaign.CampaignID==campaign_ID)
                      .join(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
                      .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
                      .one())
    return render_template('Admin_campaign_details.html',camp=camp,spon=spon,inf=inf,admin_ID=admin_ID)


@app.route('/admin/sponsors/<int:admin_ID>',methods=['GET'])
@login_required(role='admin')
def admin_sponsors(admin_ID):
    sponsors=(db.session.query(Sponsor,func.sum(Campaign.Budget),func.sum(Campaign.Outreach),func.count(Campaign.CampaignID))
                .outerjoin(Campaign,Campaign.SponsorID==Sponsor.SponsorID)
                .group_by(Sponsor.SponsorID)
                .order_by(Sponsor.SponsorID).all())
    return render_template('Admin_sponsors.html',admin_ID=admin_ID,sponsors=sponsors)

@app.route('/admin/sponsor/sponsor_details/<int:admin_ID>/<sponsor_ID>',methods=['GET'])
@login_required(role='admin')
def admin_sponsor_details(admin_ID,sponsor_ID):
    sponsor_campaign=(db.session.query(Sponsor,func.count(Campaign.CampaignID))
                      .filter(Sponsor.SponsorID==sponsor_ID)
                      .join(Campaign,Campaign.SponsorID==Sponsor.SponsorID)
                      .one())
    (spon,campaigns)=sponsor_campaign
    return render_template('Admin_sponsor_details.html',admin_ID=admin_ID,spon=spon,campaigns=campaigns)

@app.route('/admin/sponsor/flag_unflag/<int:admin_ID>/<sponsor_ID>',methods=['POST'])
@login_required(role='admin')
def admin_sponsor_flag(admin_ID,sponsor_ID):
    sponsor=db.session.query(Sponsor).filter(Sponsor.SponsorID==sponsor_ID).one()
    action=request.form['action']
    if action == 'Flag':
            sponsor.Flagged = 1
    elif action == 'Unflag':
        sponsor.Flagged = 0
    new_log=AdminLogs(
        AdminID=admin_ID,
        Action=action,
        Message=f'{action} -> Sponsor: {sponsor.SponsorID}({sponsor.Name})'
    )    
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('admin_sponsor_details', admin_ID=admin_ID, sponsor_ID=sponsor_ID))

@app.route('/admin/sponsor/sponsor_campaigns/<int:admin_ID>/<sponsor_ID>',methods=['GET'])
@login_required(role='admin')
def admin_sponsor_campaigns(admin_ID,sponsor_ID):
    from datetime import datetime
    today=datetime.today()
    active=(db.session.query(Sponsor,Influencer,Campaign)
            .filter(Sponsor.SponsorID==sponsor_ID)
            .join(Campaign,Campaign.SponsorID==Sponsor.SponsorID)
            .join(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
            .filter(Campaign.EndDate>=today)
            .order_by(Campaign.EndDate)
            .all())
    completed=(db.session.query(Sponsor,Influencer,Campaign)
            .filter(Sponsor.SponsorID==sponsor_ID)
            .join(Campaign,Campaign.SponsorID==Sponsor.SponsorID)
            .join(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
            .filter(Campaign.EndDate<today)
            .order_by(Campaign.EndDate)
            .all())
    return render_template('Admin_sponsor_campaigns.html',admin_ID=admin_ID,sponsor_ID=sponsor_ID,active=active,completed=completed)

@app.route('/admin/influencers/<int:admin_ID>', methods=['GET'])
@login_required(role='admin')
def admin_influencers(admin_ID):
    influencers = (db.session.query(Influencer, func.coalesce(func.sum(Campaign.Budget), 0), func.coalesce(func.count(Campaign.CampaignID), 0))
                   .outerjoin(Campaign, Campaign.InfluencerID == Influencer.InfluencerID)
                   .group_by(Influencer.InfluencerID)
                   .order_by(Influencer.InfluencerID).all())
    return render_template('Admin_influencers.html', admin_ID=admin_ID, influencers=influencers)

@app.route('/admin/influencer/influencer_details/<int:admin_ID>/<influencer_ID>',methods=['GET'])
@login_required(role='admin')
def admin_influencer_details(admin_ID,influencer_ID):
    influencer_campaign=(db.session.query(Influencer,func.count(Campaign.CampaignID),func.sum(Campaign.Budget))
                      .filter(Influencer.InfluencerID==influencer_ID)
                      .join(Campaign,Campaign.InfluencerID==Influencer.InfluencerID)
                      .one())
    (inf,campaigns,earnings)=influencer_campaign
    return render_template('Admin_influencer_details.html',admin_ID=admin_ID,inf=inf,campaigns=campaigns,earnings=earnings)

@app.route('/admin/influencer/flag_unflag/<int:admin_ID>/<influencer_ID>',methods=['POST'])
@login_required(role='admin')
def admin_influencer_flag(admin_ID,influencer_ID):
    influencer=db.session.query(Influencer).filter(Influencer.InfluencerID==influencer_ID).one()
    action=request.form['action']
    if action == 'Flag':
            influencer.Flagged = 1
    elif action == 'Unflag':
        influencer.Flagged = 0
    new_log=AdminLogs(
        AdminID=admin_ID,
        Action=action,
        Message=f'{action} -> Influencer: {influencer.InfluencerID}({influencer.Name})'
    )    
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('admin_influencer_details', admin_ID=admin_ID, influencer_ID=influencer_ID))

@app.route('/admin/influencer/influencer_campaigns/<int:admin_ID>/<influencer_ID>',methods=["GET"])
@login_required(role='admin')
def admin_influencer_campaigns(admin_ID,influencer_ID):
    from datetime import datetime
    today=datetime.today()
    active=(db.session.query(Influencer,Sponsor,Campaign)
            .filter(Influencer.InfluencerID==influencer_ID)
            .join(Campaign,Campaign.InfluencerID==Influencer.InfluencerID)
            .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
            .filter(Campaign.EndDate>=today)
            .order_by(Campaign.EndDate)
            .all())
    completed=(db.session.query(Influencer,Sponsor,Campaign)
            .filter(Influencer.InfluencerID==influencer_ID)
            .join(Campaign,Campaign.InfluencerID==Influencer.InfluencerID)
            .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
            .filter(Campaign.EndDate<today)
            .order_by(Campaign.EndDate)
            .all())
    return render_template('Admin_influencer_campaigns.html',admin_ID=admin_ID,active=active,completed=completed,influencer_ID=influencer_ID)



