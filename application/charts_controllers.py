from flask import Flask, render_template,redirect,url_for,flash,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from application.models import*
from application.home_controllers import login_required
from application import engine
import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # Use the Agg backend
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

spon_query = f"SELECT * FROM Sponsor"
inf_query = f"SELECT * FROM Influencer"
camp_query = f"SELECT * FROM Campaign"
inf_camp_query = f"SELECT I.InfluencerID,I.Name,C.Budget,I.JoiningDate,C.StartDate FROM Influencer I JOIN Campaign C ON I.InfluencerID=C.InfluencerID"
spon_camp_query = f"SELECT S.SponsorID,S.Name,C.Outreach,S.JoiningDate,C.StartDate FROM Sponsor S JOIN Campaign C ON S.SponsorID=C.SponsorID"

spon_df = pd.read_sql(spon_query, engine)
inf_df = pd.read_sql(inf_query, engine)
camp_df = pd.read_sql(camp_query, engine)
inf_camp_df=pd.read_sql(inf_camp_query,engine)
spon_camp_df=pd.read_sql(spon_camp_query,engine)

inf_df['JoiningDate']=pd.to_datetime(inf_df['JoiningDate'])
spon_df['JoiningDate']=pd.to_datetime(spon_df['JoiningDate'])
camp_df['StartDate']=pd.to_datetime(camp_df['StartDate'])
camp_df['EndDate']=pd.to_datetime(camp_df['EndDate'])
inf_camp_df['StartDate']=pd.to_datetime(inf_camp_df['StartDate'])
spon_camp_df['StartDate']=pd.to_datetime(spon_camp_df['StartDate'])

def path(link):
    image_path = 'static/images/Statistics'
    abs_path = os.path.abspath(image_path)
    full_path = os.path.join(abs_path, link)
    return full_path



def quarterly_outreach(link):
    quarterly_summary = camp_df.groupby(pd.Grouper(key='EndDate', freq='QE'))['Outreach'].sum()
    filtered_summary = quarterly_summary[quarterly_summary > 0]

    plt.figure(figsize=(8, 8))
    plt.title("Quarterly Outreach")
    plt.xlabel("Quarter")
    plt.ylabel("Outreach")
    plt.xticks(
        ticks=filtered_summary.index,
        labels=[f'Q{(x.month-1)//3 + 1}-{x.year}' for x in filtered_summary.index],
        rotation=45
    )
    plt.bar(filtered_summary.index, filtered_summary.values, width=90)  
    plt.tight_layout()  
    plt.savefig(path(link))
    plt.close()

def quarterly_revenue(link):
    quarterly_summary = camp_df.groupby(pd.Grouper(key='EndDate', freq='QE'))['Budget'].sum()
    filtered_summary = quarterly_summary[quarterly_summary > 0]

    plt.figure(figsize=(8, 8))
    plt.title("Quarterly Revenue")
    plt.xlabel("Quarter")
    plt.ylabel("Budget")
    plt.xticks(
        ticks=filtered_summary.index,
        labels=[f'Q{(x.month-1)//3 + 1}-{x.year}' for x in filtered_summary.index],
        rotation=45
    )
    plt.bar(filtered_summary.index, filtered_summary.values, width=90)  
    plt.tight_layout()  
    plt.savefig(path(link))
    plt.close()

def top_earners(link):
    top_earners = (inf_camp_df.groupby(['InfluencerID', 'Name'])['Budget'].sum().reset_index())
    top_earners = top_earners[['Name', 'Budget']].sort_values(by='Budget', ascending=False).head(10)

    plt.figure(figsize=(8, 8))
    plt.title("Top Earners")
    plt.xlabel("Name")
    plt.ylabel("Earnings")
    plt.xticks(rotation=45)
    plt.bar(top_earners['Name'], top_earners['Budget'], width=0.95)  
    plt.savefig(path(link))
    plt.close()
    
def top_gainers(link):
    top_gainers=(spon_camp_df.groupby(['SponsorID','Name'])['Outreach'].sum().reset_index())
    top_gainers=top_gainers[['Name','Outreach']].sort_values(by='Outreach',ascending=False).head(10)

    plt.figure(figsize=(8, 8))
    plt.title("Top Gainers")
    plt.xlabel("Name")
    plt.ylabel("Outreach Gained")
    plt.xticks(rotation=45)
    plt.bar(top_gainers['Name'], top_gainers['Outreach'], width=0.95)  
    plt.savefig(path(link))
    plt.close()

def active_inf(link):
    current=datetime.today()
    active=current-pd.DateOffset(months=3)
    active_users=len(inf_camp_df[inf_camp_df['StartDate']>=active])
    total_users=len(inf_camp_df)

    sizes = [active_users, total_users - active_users]
    labels = ['Active', 'Inactive']

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, autopct='%1.1f%%', colors=['#4caf50', '#f44336'])
    plt.legend(labels, title='User Status', loc='best')
    plt.title('Active Influencers')
    plt.savefig(path(link))
    plt.close()

def active_spon(link):
    current=datetime.today()
    active=current-pd.DateOffset(months=3)
    active_users=len(spon_camp_df[spon_camp_df['StartDate']>=active])
    total_users=len(spon_camp_df)

    sizes = [active_users, total_users - active_users]
    labels = ['Active', 'Inactive']

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, autopct='%1.1f%%', colors=['#4caf50', '#f44336'])
    plt.legend(labels, title='User Status', loc='best')
    plt.title('Active Sponsors')
    plt.savefig(path(link))
    plt.close()

def num_inf(link):
    num_inf=inf_df.groupby(pd.Grouper(key='JoiningDate',freq='QE'))['InfluencerID'].count()

    plt.figure(figsize=(8, 8))
    plt.title("New Influencers")
    plt.xlabel("Quarter")
    plt.ylabel("No. of Joiners")
    plt.xticks(
        ticks=num_inf.index,
        labels=[f'Q{(x.month-1)//3 + 1}-{x.year}' for x in num_inf.index],
        rotation=45
    )
    plt.bar(num_inf.index, num_inf.values, width=90)  
    plt.tight_layout()  
    plt.savefig(path(link))
    plt.close()

def num_spon(link):
    num_spon=spon_df.groupby(pd.Grouper(key='JoiningDate',freq='QE'))['SponsorID'].count()

    plt.figure(figsize=(8, 8))
    plt.title("New Sponsors")
    plt.xlabel("Quarter")
    plt.ylabel("No. of Joiners")
    plt.xticks(
        ticks=num_spon.index,
        labels=[f'Q{(x.month-1)//3 + 1}-{x.year}' for x in num_spon.index],
        rotation=45
    )
    plt.bar(num_spon.index, num_spon.values, width=90)  
    plt.tight_layout()  
    plt.savefig(path(link))
    plt.close()

def num_camp(link):
    num_camp=camp_df.groupby(pd.Grouper(key='StartDate',freq='QE'))['CampaignID'].count()

    plt.figure(figsize=(8, 8))
    plt.title("New Campaigns")
    plt.xlabel("Quarter")
    plt.ylabel("No. of Campaigns")
    plt.xticks(
        ticks=num_camp.index,
        labels=[f'Q{(x.month-1)//3 + 1}-{x.year}' for x in num_camp.index],
        rotation=45
    )
    plt.bar(num_camp.index, num_camp.values, width=90)  
    plt.tight_layout()  
    plt.savefig(path(link))
    plt.close()

def campaign_outreach(sponsor_ID, link):
    query = """
    SELECT C.Name, C.Outreach 
    FROM Sponsor S 
    JOIN Campaign C ON S.SponsorID = C.SponsorID 
    WHERE S.SponsorID = ?
    ORDER BY C.StartDate
    """
    df = pd.read_sql(query, engine, params=(sponsor_ID,))

    plt.figure(figsize=(10, 6))
    plt.bar(df['Name'], df['Outreach'], color='#4caf50', edgecolor='black', width=0.8)
    
    plt.title("Campaign Wise Outreach Gained", fontsize=16, fontweight='bold')
    plt.xlabel("Campaign", fontsize=12, fontweight='bold')
    plt.ylabel("Outreach", fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(path(link))
    plt.close()

@app.route('/admin/statistics/<int:admin_ID>',methods=["GET"])
@login_required(role='admin')
def admin_statistics(admin_ID):
    outreach='quarterly_outreach.png'
    revenue='quarterly_revenue.png'
    top_earning='top_earners.png'
    top_gains='top_gainers.png'
    active_infs='active_inf.png'
    active_spons='active_spon.png'
    quarterly_outreach(outreach)
    quarterly_revenue(revenue)
    top_earners(top_earning)
    top_gainers(top_gains)
    active_inf(active_infs)
    active_spon(active_spons)
    return render_template('Admin_statistics.html',admin_ID=admin_ID)
