from flask import Flask, render_template,redirect,url_for,flash,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from application.models import*
from application.home_controllers import login_required
from datetime import datetime

@app.route('/sponsor/ad_req/create/<int:sponsor_ID>/<int:campaign_ID>', methods=['GET', 'POST'])
@login_required(role='sponsor')
def create_request(sponsor_ID, campaign_ID):
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        requirements = request.form['requirements']
        payment = float(request.form['payment']) 
        influencer_ids = request.form.getlist('influencers')  

        new_request = AdRequest(
            Title=title,
            Description=message,
            Requirements=requirements,
            Payment=payment,
            CampaignID=campaign_ID,
            Status='Pending' 
        )
        db.session.add(new_request)
        db.session.commit()

        for influencer_id in influencer_ids:
            ad_negotiation = AdNegotiation(
                RequestID=new_request.RequestID,
                InfluencerID=influencer_id,
                Current_Negotiation=float(new_request.Payment),  
                Sender='Sponsor', 
                Time=datetime.now(),
                Status='Open'
            )
            db.session.add(ad_negotiation)
        db.session.commit()
        return redirect(f'/sponsor/ad_req/view/{sponsor_ID}/{campaign_ID}')
    elif request.method == 'GET':
        all_influencers = Influencer.query.order_by(Influencer.Followers.desc()).all()
        return render_template('Ad_create.html', sponsor_ID=sponsor_ID, campaign_ID=campaign_ID, all_influencers=all_influencers)


@app.route('/sponsor/ad_req/view/<int:sponsor_ID>/<campaign_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_view_requests(sponsor_ID,campaign_ID):
    ad_requests=(db.session.query(AdRequest,Campaign)
                 .join(Campaign,Campaign.CampaignID==AdRequest.CampaignID)
                 .filter(Campaign.CampaignID==campaign_ID)
                 .all())
    return render_template('Ad_view_all.html',ad_requests=ad_requests,sponsor_ID=sponsor_ID,campaign_ID=campaign_ID)

@app.route('/sponsor/ad_req/edit/<int:sponsor_ID>/<request_ID>',methods=['GET','POST'])
@login_required(role='sponsor')
def edit_request(sponsor_ID,request_ID):
    ad_request=db.session.query(AdRequest).filter(AdRequest.RequestID==request_ID).one()
    if request.method=='POST':
        ad_request.Description=request.form['Description']
        ad_request.Payment=request.form['Payment']
        ad_request.Requirements=request.form['Requirements']
        db.session.add(ad_request)
        db.session.commit()
        return redirect(f'/sponsor/ad_req/view/{ sponsor_ID }/{ad_request.CampaignID}')
    return render_template('Ad_edit.html',sponsor_ID=sponsor_ID,ad_request=ad_request)

@app.route('/sponsor/ad_req/delete/<int:sponsor_ID>/<request_ID>', methods=["POST"])
@login_required(role='sponsor')
def sponsor_ad_delete(sponsor_ID, request_ID):
    # Fetch the campaign to be deleted
    ad_request = db.session.query(AdRequest).filter(AdRequest.RequestID==request_ID).one()
    campaign_id=ad_request.CampaignID
    db.session.delete(ad_request)
    db.session.commit()
    return redirect(f'/sponsor/ad_req/view/{sponsor_ID}/{campaign_id}')

@app.route('/sponsor/send_req/<int:sponsor_ID>/<influencer_ID>',methods=['GET','POST'])
@login_required(role='sponsor')
def send_req(sponsor_ID,influencer_ID):
    today=datetime.today()
    if request.method=='GET':
        campaigns=db.session.query(Campaign).filter(Campaign.SponsorID==sponsor_ID,Campaign.EndDate>=today,Campaign.InfluencerID==None).all()
        return render_template('Ad_send.html',sponsor_ID=sponsor_ID,influencer_ID=influencer_ID,campaigns=campaigns)
    if request.method=='POST':
        title=request.form['title']
        description=request.form['description']
        requirements=request.form['requirements']
        payment=request.form['payment']
        campaignID=request.form.get('campaignID')
        status=request.form['status']
        new_ad=AdRequest(
            Title=title,
            Description=description,
            Requirements=requirements,
            Payment=payment,
            CampaignID=campaignID,
            Status=status
        )
        db.session.add(new_ad)
        db.session.commit()
        new_negotiation=AdNegotiation(
            RequestID=new_ad.RequestID,
            InfluencerID=int(influencer_ID),
            Current_Negotiation=float(new_ad.Payment),
            Status='Open',
            Sender='Sponsor',
            Time=datetime.now().replace(microsecond=0)
        )
        db.session.add(new_negotiation)
        db.session.commit()
        return redirect(url_for('sponsor_influencers',sponsor_ID=sponsor_ID))
   

@app.route('/influencer/ad_req/view/<int:influencer_ID>/<adreq_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_view_requests(influencer_ID,adreq_ID):
    ad_req=db.session.query(AdNegotiation).filter(AdNegotiation.InfluencerID==influencer_ID,AdNegotiation.RequestID==adreq_ID).one()
    ad=ad_req.ad_request
    return render_template('Ad_inf_view.html',ad_request=ad,influencer_ID=influencer_ID,ad=ad_req)
    
@app.route('/ad_request/influencer_accept/<int:influencer_ID>/<request_ID>', methods=['POST'])
@login_required(role='influencer')
def influencer_accept_request(influencer_ID, request_ID):
    ad_req = db.session.query(AdRequest).filter(AdRequest.RequestID == request_ID).one()
    final_neg=db.session.query(AdNegotiation).filter(AdNegotiation.RequestID==request_ID,AdNegotiation.InfluencerID==influencer_ID).one()
    ad_req.Status = 'Accepted'    
    ad_req.campaign.InfluencerID = influencer_ID
    ad_req.campaign.Outreach = final_neg.influencer.Followers
    ad_req.campaign.Budget = final_neg.Current_Negotiation
    ad_req.Payment=final_neg.Current_Negotiation
    camps = db.session.query(AdRequest).filter(
        AdRequest.CampaignID == ad_req.CampaignID,
        AdRequest.RequestID != ad_req.RequestID
    ).all()
    for i in camps:
        i.Status = 'Closed'
        db.session.add(i)
    nego = db.session.query(AdNegotiation).filter(
        AdNegotiation.RequestID == ad_req.RequestID
    ).all()
    for i in nego:
        if i.InfluencerID == int(influencer_ID):
            i.Status = 'Accepted'
        else:
            i.Status = 'Closed'
        db.session.add(i)
    ad_req.campaign.Budget=ad_req.Payment
    db.session.add(ad_req)
    db.session.commit()
    return redirect(f'/influencer/campaigns/{influencer_ID}')

@app.route('/ad_request/influencer_reject/<int:influencer_ID>/<request_ID>',methods=['POST'])
@login_required(role='influencer')
def influencer_reject_request(influencer_ID,request_ID):
    nego=db.session.query(AdNegotiation).filter(AdNegotiation.RequestID==request_ID,AdNegotiation.InfluencerID==influencer_ID).one()
    nego.Status='Rejected'
    db.session.commit()
    return redirect(f'/influencer/campaigns/{influencer_ID}')

@app.route('/ad_request/influencer_negotiate/<int:influencer_ID>/<request_ID>',methods=['GET','POST'])
@login_required(role='influencer')
def influencer_negotiate_request(influencer_ID,request_ID):
    nego=db.session.query(AdNegotiation).filter(AdNegotiation.RequestID==request_ID,AdNegotiation.InfluencerID==influencer_ID).one()
    if request.method=='GET':
        req=nego.ad_request
        return render_template('Ad_Inf_Negotiation.html',ad_request=req,influencer_ID=influencer_ID,ad=nego)
    if request.method=='POST':
        nego.Current_Negotiation=request.form.get('proposed_payment')
        nego.Sender='Influencer'
        nego.Time=datetime.now().replace(microsecond=0)
        db.session.commit()
        return redirect(f'/influencer/campaigns/{influencer_ID}')
        
@app.route('/sponsor/ad_request/negotiations/view/<int:sponsor_ID>/<request_ID>/<influencer_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_view(sponsor_ID,request_ID,influencer_ID):
    ad_req=db.session.query(AdNegotiation).filter(AdNegotiation.InfluencerID==influencer_ID,AdNegotiation.RequestID==request_ID).one()
    ad=ad_req.ad_request
    return render_template('Ad_spon_view.html',ad_request=ad,influencer_ID=influencer_ID,ad=ad_req,sponsor_ID=sponsor_ID)
    
@app.route('/ad_request/sponsor_accept/<int:sponsor_ID>/<influencer_ID>/<request_ID>', methods=['POST'])
@login_required(role='sponsor')
def sponsor_accept_request(sponsor_ID,influencer_ID, request_ID):
    ad_req = db.session.query(AdRequest).filter(AdRequest.RequestID == request_ID).one()
    final_neg=db.session.query(AdNegotiation).filter(AdNegotiation.RequestID==request_ID,AdNegotiation.InfluencerID==influencer_ID).one()
    ad_req.Status = 'Accepted'    
    ad_req.campaign.InfluencerID = influencer_ID
    ad_req.campaign.Outreach = final_neg.influencer.Followers
    ad_req.campaign.Budget = final_neg.Current_Negotiation
    ad_req.Payment=final_neg.Current_Negotiation
    camps = db.session.query(AdRequest).filter(
        AdRequest.CampaignID == ad_req.CampaignID,
        AdRequest.RequestID != ad_req.RequestID
    ).all()
    for i in camps:
        i.Status = 'Closed'
        db.session.add(i)
    nego = db.session.query(AdNegotiation).filter(
        AdNegotiation.RequestID == ad_req.RequestID
    ).all()
    for i in nego:
        if i.InfluencerID == int(influencer_ID):
            i.Status = 'Accepted'
        else:
            i.Status = 'Closed'
        db.session.add(i)
    ad_req.campaign.Budget=ad_req.Payment
    db.session.add(ad_req)
    db.session.commit()
    return redirect(f'/sponsor/home/{sponsor_ID}')

@app.route('/ad_request/sponsor_reject/<int:sponsor_ID>/<influencer_ID>/<request_ID>',methods=['POST'])
@login_required(role='sponsor')
def sponsor_reject_request(sponsor_ID,influencer_ID,request_ID):
    nego=db.session.query(AdNegotiation).filter(AdNegotiation.RequestID==request_ID,AdNegotiation.InfluencerID==influencer_ID).one()
    nego.Status='Rejected'
    db.session.commit()
    return redirect(f'/sponsor/campaigns/{sponsor_ID}')

@app.route('/ad_request/sponsor_negotiate/<int:sponsor_ID>/<influencer_ID>/<request_ID>', methods=['GET', 'POST'])
@login_required(role='sponsor')
def sponsor_negotiate_request(sponsor_ID, influencer_ID, request_ID):
    nego = db.session.query(AdNegotiation).filter(AdNegotiation.RequestID == request_ID,AdNegotiation.InfluencerID == influencer_ID).one()
    
    if request.method == 'GET':
        req = nego.ad_request
        ad = nego
        return render_template('Ad_Spon_Negotiation.html', ad_request=req, influencer_ID=influencer_ID, ad=nego,sponsor_ID=sponsor_ID)
    
    if request.method == 'POST':
        nego.Current_Negotiation = request.form.get('proposed_payment')
        nego.Sender = 'Sponsor'
        nego.Time = datetime.now().replace(microsecond=0)
        db.session.commit()
        return redirect(f'/sponsor/campaigns/{sponsor_ID}')
@app.route('/sponsor/ad_request/view_all/<int:sponsor_ID>',methods=['GET'])
@login_required(role='sponsor')
def sponsor_view_adreqs(sponsor_ID):
    negotiations = (db.session.query(AdNegotiation)
                .join(AdNegotiation.ad_request)  
                .join(AdRequest.campaign)  
                .filter(Campaign.SponsorID == sponsor_ID) 
                .filter(AdNegotiation.Status=='Open') 
                .order_by(AdNegotiation.Time.desc())
                .all()) 
    return render_template('Ad_spon_viewall.html',negotiations=negotiations,sponsor_ID=sponsor_ID)


@app.route('/influencer/ad_request/view_all/<int:influencer_ID>',methods=['GET'])
@login_required(role='influencer')
def influencer_view_adreqs(influencer_ID):
    subquery = (
    db.session.query(AdNegotiation.RequestID)
    .join(Influencer, AdNegotiation.InfluencerID == Influencer.InfluencerID)
    .filter(Influencer.InfluencerID == 5)
    .distinct()
    )
    requests = (
        db.session.query(AdRequest)
        .join(Campaign, Campaign.CampaignID == AdRequest.CampaignID)
        .filter(
            Campaign.Visibility == 'Public',
            AdRequest.Status == 'Pending',
            ~AdRequest.RequestID.in_(subquery)
        )
        .all()
    )
    return render_template('Ad_inf_viewall.html',ad_requests=requests,influencer_ID=influencer_ID)

@app.route('/influencer/apply/<int:influencer_ID>/<request_ID>',methods=["POST"])
@login_required(role='influencer')
def influencer_apply(influencer_ID,request_ID):
    
    ad_req=db.session.query(AdRequest).filter(AdRequest.RequestID==request_ID).one()
    ad_nego=AdNegotiation(
        RequestID=request_ID,
        InfluencerID=influencer_ID,
        Current_Negotiation=ad_req.Payment,
        Sender='Sponsor',
        Time=datetime.now().replace(microsecond=0),
        Status='Open'
    )
    db.session.add(ad_nego)
    db.session.commit()
    return redirect(f'/influencer/ad_request/view_all/{influencer_ID}')

@app.route('/ad_request/influencer/create_negotiation/<int:influencer_ID>/<request_ID>',methods=['GET','POST'])
@login_required(role='influencer')
def create_negotiation(influencer_ID,request_ID):
    ad_request=db.session.query(AdRequest).filter(AdRequest.RequestID==request_ID).one()
    if request.method=='GET':
        return render_template('Ad_create_negotiation.html',ad_request=ad_request,influencer_ID=influencer_ID)
    elif request.method=='POST':
        new_nego=AdNegotiation(
            RequestID=request_ID,
            InfluencerID=influencer_ID,
            Current_Negotiation=request.form['proposed_payment'],
            Sender='Influencer',
            Time=datetime.now().replace(microsecond=0),
            Status='Open'
        )
        db.session.add(new_nego)
        db.session.commit()
        return redirect(f'/influencer/ad_request/view_all/{influencer_ID}')
