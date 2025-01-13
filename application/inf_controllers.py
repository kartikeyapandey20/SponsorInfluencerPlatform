from flask import Flask, render_template,redirect,url_for,flash,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from application.models import*
from application.home_controllers import login_required

@app.route('/influencer/home/<int:influencer_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_home(influencer_ID):
    influencer=db.session.query(Influencer).filter(Influencer.InfluencerID==influencer_ID).one()
    return render_template('influencer_home.html',influencer=influencer)

@app.route('/influencer/profile/<int:influencer_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_profile(influencer_ID):
    influencer=db.session.query(Influencer).filter(Influencer.InfluencerID==influencer_ID).one()
    return render_template('influencer_Profile.html',influencer=influencer)

@app.route('/influencer/profile/edit/<int:influencer_ID>',methods=['GET','POST'])
@login_required(role='influencer')
def influencer_profile_edit(influencer_ID):
    influencer=db.session.query(Influencer).filter(Influencer.InfluencerID==influencer_ID).one()
    if request.method=='GET':
        return render_template('Influencer_profile_edit.html',influencer=influencer)
    elif request.method=='POST':
        influencer.Email=request.form['email']
        influencer.PhoneNo=request.form['phone']
        influencer.Bio=request.form['bio']
        db.session.add(influencer)
        db.session.commit()
        return redirect(f'/influencer/profile/{influencer_ID}',code=302)
    


@app.route('/influencer/campaigns/<int:influencer_ID>',methods=["GET"])
@login_required(role='influencer')
def influencer_campaigns(influencer_ID):
    from datetime import datetime,timedelta
    today=datetime.today()
    influencer=db.session.query(Influencer).filter(Influencer.InfluencerID==influencer_ID).one()
    active_campaigns=(db.session.query(Campaign,Sponsor)
                      .filter(Campaign.InfluencerID==influencer.InfluencerID,Campaign.EndDate>=today)
                      .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
                      .all())
    completed_campaigns=(db.session.query(Campaign,Sponsor)
                      .filter(Campaign.InfluencerID==influencer.InfluencerID,Campaign.EndDate<today)
                      .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
                      .all())
    top_campaigns=db.session.query(Campaign).filter(Campaign.InfluencerID==influencer.InfluencerID).order_by(Campaign.Budget.desc()).limit(3).all()
    top_sponsors = (
    db.session.query(Sponsor)
    .select_from(Campaign)
    .filter(Campaign.InfluencerID == influencer.InfluencerID)
    .join(Sponsor, Campaign.SponsorID == Sponsor.SponsorID)
    .order_by(Campaign.Budget.desc())
    .limit(3)
    .all()
    )
    threemonth_earnings=(
        db.session.query(func.sum(Campaign.Budget))
        .filter(Campaign.InfluencerID==influencer.InfluencerID,
                Campaign.EndDate<=today,
                Campaign.EndDate>=(today-timedelta(days=90))
                )
        .scalar())
    ad_req=db.session.query(AdNegotiation).filter(AdNegotiation.InfluencerID==influencer.InfluencerID,AdNegotiation.Status=='Open').all()
    return render_template('influencer_campaigns.html',active=active_campaigns,complete=completed_campaigns,top_campaigns=top_campaigns,top_sponsors=top_sponsors,influencer=influencer,threemonth_earnings=threemonth_earnings,requests=ad_req)

@app.route('/influencer/campaigns/top/<int:influencer_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_top_campaigns(influencer_ID):
    influencer=db.session.query(Influencer).filter(Influencer.InfluencerID==influencer_ID).one()
    top=(db.session.query(Campaign,Sponsor)
                   .filter(Campaign.InfluencerID==influencer.InfluencerID)
                   .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
                   .order_by(Campaign.Budget.desc()).all())
    return render_template('influencer_top_campaigns.html',top=top,influencer_ID=influencer_ID)

@app.route('/influencer/campaign/campaign_details/<int:influencer_ID>/<campaign_ID>',methods=["GET"])
@login_required(role='influencer')
def influencer_campaign_details(influencer_ID,campaign_ID):
    spon_camps=(db.session.query(Sponsor,Campaign)
          .filter(Campaign.CampaignID==campaign_ID)
          .join(Sponsor,Campaign.SponsorID==Sponsor.SponsorID)
          .one())
    (spon,camp)=(spon_camps)
    return render_template('influencer_campaign_details.html',sponsor=spon,campaign=camp,influencer_ID=influencer_ID)

@app.route('/influencer/sponsor/<int:influencer_ID>/<sponsor_ID>',methods=["GET"])
@login_required(role='influencer')
def influencer_sponsor_details(sponsor_ID,influencer_ID):
    sponsor = db.session.query(Sponsor).filter(Sponsor.SponsorID == sponsor_ID).one()
    total_campaigns=db.session.query(Campaign).filter(Campaign.SponsorID==sponsor_ID).count()
    associations=db.session.query(Campaign).filter(Campaign.SponsorID==sponsor_ID,Campaign.InfluencerID==influencer_ID).all()
    return render_template('influencer_sponsor_details.html',sponsor=sponsor,Associations=associations,total_campaigns=total_campaigns,influencer_ID=influencer_ID)

@app.route('/influencer/sponsor/top/<int:influencer_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_top_sponsors(influencer_ID):
    top = (
    db.session.query(Sponsor,Campaign)
    .filter(Campaign.InfluencerID == influencer_ID)
    .join(Sponsor, Campaign.SponsorID == Sponsor.SponsorID)
    .order_by(Campaign.Budget.desc())
    .all()
    )
    return render_template('influencer_Top_sponsors.html',influencer_ID=influencer_ID,top=top)

@app.route('/influencer/earnings/<int:influencer_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_earnings(influncer_ID):
    return render_template('influencer_Earnings.html')