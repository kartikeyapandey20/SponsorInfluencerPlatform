from flask import Flask, render_template,redirect,url_for,flash,request
from flask_sqlalchemy import SQLAlchemy
from application.models import*
from datetime import datetime
from application.home_controllers import login_required
from application.charts_controllers import campaign_outreach

@app.route('/sponsor/home/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_home(sponsor_ID):
    chart_link=f'CampaignOutreach{sponsor_ID}.png'
    sponsor=db.session.query(Sponsor).filter(Sponsor.SponsorID==sponsor_ID).one()
    campaign_outreach(sponsor.SponsorID,chart_link)
    return render_template('Sponsor_Home.html',sponsor=sponsor)

@app.route('/sponsor/profile/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_profile(sponsor_ID):
    sponsor=db.session.query(Sponsor).filter(Sponsor.SponsorID==sponsor_ID).one()
    return render_template('Sponsor_Profile.html',sponsor=sponsor)

@app.route('/sponsor/profile/edit/<int:sponsor_ID>',methods=['GET','POST'])
@login_required(role='sponsor')
def sponsor_profile_edit(sponsor_ID):
    sponsor=db.session.query(Sponsor).filter(Sponsor.SponsorID==sponsor_ID).one()
    if request.method=='GET':
        return render_template('Sponsor_profile_edit.html',sponsor=sponsor)
    elif request.method=='POST':
        sponsor.Brand=request.form['brand']
        sponsor.Email=request.form['email']
        sponsor.PhoneNo=request.form['phone']
        sponsor.BrandDescription=request.form['description']
        db.session.add(sponsor)
        db.session.commit()
        return redirect(f'/sponsor/profile/{sponsor_ID}', code=302)

@app.route('/sponsor/campaigns/<int:sponsor_ID>',methods=["GET"])
@login_required(role='sponsor')
def sponsor_campaigns(sponsor_ID):
    from datetime import datetime
    today=datetime.today()
    sponsor=db.session.query(Sponsor).filter(Sponsor.SponsorID==sponsor_ID).one()
    active_campaigns=(db.session.query(Campaign,Influencer)
                      .filter(Campaign.SponsorID==sponsor.SponsorID,Campaign.EndDate>=today)
                      .outerjoin(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
                      .all())
    completed_campaigns=(db.session.query(Campaign,Influencer)
                         .filter(Campaign.SponsorID==sponsor.SponsorID,Campaign.EndDate<today)
                         .outerjoin(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
                         .all())
    top_campaigns=db.session.query(Campaign).filter(Campaign.SponsorID==sponsor.SponsorID).order_by(Campaign.Outreach.desc()).limit(3).all()
    highest=db.session.query(Campaign).filter(Campaign.SponsorID==sponsor.SponsorID).order_by(Campaign.Outreach.desc()).first()
    top_infs = (
    db.session.query(Influencer)
    .select_from(Campaign)
    .filter(Campaign.SponsorID == sponsor.SponsorID)
    .join(Influencer, Campaign.InfluencerID == Influencer.InfluencerID)
    .order_by(Campaign.Outreach.desc())
    .limit(3)
    .all()
    )
    return render_template('sponsor_campaigns.html',active=active_campaigns,complete=completed_campaigns,top_campaigns=top_campaigns,highest=highest,top_infs=top_infs,sponsor=sponsor)

@app.route('/sponsor/campaigns/top/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_top_campaigns(sponsor_ID):
    sponsor=db.session.query(Sponsor).filter(Sponsor.SponsorID==sponsor_ID).one()
    top=(db.session.query(Campaign,Influencer)
                   .filter(Campaign.SponsorID==sponsor.SponsorID)
                   .join(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
                   .order_by(Campaign.Outreach.desc()).all())
    return render_template('sponsor_top_campaigns.html',top=top,sponsor_ID=sponsor_ID)

@app.route('/sponsor/campaign/create/<int:sponsor_ID>', methods=['GET', 'POST'])
@login_required(role='sponsor')
def sponsor_campaign_create(sponsor_ID):
    sponsor_ID = int(sponsor_ID)
    if request.method == 'GET':
        return render_template('sponsor_create_campaign.html', sponsor_ID=sponsor_ID)
    
    elif request.method == 'POST':
        name = request.form['campaignName']
        desc = request.form['description']
        startDate = datetime.strptime(request.form['startDate'], '%Y-%m-%d').date()
        endDate = datetime.strptime(request.form['endDate'], '%Y-%m-%d').date()
        Budget = request.form['Budget']
        goal = request.form['goals']
        visibility = request.form['visibility']
        campaign_data = Campaign(
            Name=name,
            Description=desc,
            StartDate=startDate,
            EndDate=endDate,
            Budget=Budget,
            Goal=goal,
            Visibility=visibility,
            SponsorID=sponsor_ID  # Ensure correct ID is used
        )
        db.session.add(campaign_data)
        db.session.commit()
        return redirect(f'/sponsor/campaigns/{sponsor_ID}', code=302)

@app.route('/sponsor/campaign/campaign_details/<int:sponsor_ID>/<campaign_ID>',methods=["GET"])
@login_required(role='sponsor')
def sponsor_campaign_details(sponsor_ID,campaign_ID):   
    from datetime import date
    today=date.today()
    infs_camps=(db.session.query(Campaign,Influencer)
        .filter(Campaign.CampaignID==campaign_ID)
        .outerjoin(Influencer,Campaign.InfluencerID==Influencer.InfluencerID)
        .one())
    (camp,inf)=(infs_camps)
    active=None
    if camp.EndDate>=today:
        active=True
    return render_template('Sponsor_campaign_details.html',influencer=inf,campaign=camp,sponsor_ID=sponsor_ID,active=active)
  
@app.route('/sponsor/campaign/edit/<int:sponsor_ID>/<campaign_ID>',methods=["GET","POST"])
@login_required(role='sponsor')
def sponsor_campaign_edit(sponsor_ID,campaign_ID):
    campaign = Campaign.query.get(campaign_ID)
    if request.method == 'POST':
        if campaign:
            from datetime import date
            today=date.today()
            campaign.EndDate = datetime.strptime(request.form['endDate'], '%Y-%m-%d').date()
            campaign.Goal = request.form['goals']
            campaign.Visibility = request.form['visibility']
            started=campaign.StartDate<today
            if not started:
                campaign.StartDate = datetime.strptime(request.form['startDate'], '%Y-%m-%d').date()            
            if not request.form.get('influencerid'):
                campaign.Budget = request.form.get('budget')
            db.session.commit()
            return redirect(url_for('sponsor_campaign_details',campaign_ID=campaign_ID,sponsor_ID=sponsor_ID))  # Redirect to a relevant view

    return render_template('Sponsor_campaign_edit.html', campaign=campaign,sponsor_ID=sponsor_ID)


@app.route('/sponsor/campaign/delete/<int:sponsor_ID>/<campaign_ID>', methods=["POST"])
@login_required(role='sponsor')
def sponsor_campaign_delete(sponsor_ID, campaign_ID):
    # Fetch the campaign to be deleted
    campaign = db.session.query(Campaign).filter(Campaign.CampaignID == campaign_ID).one()
    db.session.delete(campaign)
    db.session.commit()
    return redirect(f'/sponsor/campaigns/{sponsor_ID}')

@app.route('/sponsor/influencers/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_influencers(sponsor_ID):
    influencers=(db.session.query(Influencer)
                 .order_by(Influencer.Followers.desc())
                 .all())
    return render_template('Sponsor_influencers.html',influencers=influencers,sponsor_ID=sponsor_ID)

@app.route('/sponsor/influencer/<int:sponsor_ID>/<influencer_ID>',methods=["GET"])
@login_required(role='sponsor')
def sponsor_influencer_details(sponsor_ID,influencer_ID):
    inf = db.session.query(Influencer).filter(Influencer.InfluencerID == influencer_ID).one()
    associations=db.session.query(Campaign).filter(Campaign.SponsorID==sponsor_ID,Campaign.InfluencerID==influencer_ID).all()
    return render_template('sponsor_influencer_details.html',inf=inf,Associations=associations,sponsor_ID=sponsor_ID)

@app.route('/sponsor/influencer/top/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_top_influencers(sponsor_ID):
    top = (
    db.session.query(Influencer,Campaign)
    .filter(Campaign.SponsorID == sponsor_ID)
    .join(Influencer, Campaign.InfluencerID == Influencer.InfluencerID)
    .order_by(Campaign.Outreach.desc())
    .all()
    )
    return render_template('sponsor_top_influencer.html',sponsor_ID=sponsor_ID,top=top)

@app.route('/sponsor/outreach/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_outreach(sponsor_ID):
    return render_template('sponsor_outreach.html')
