import React from 'react';
import RecentActivities from './RecentActivities';
import Projects from './Projects';
import WorkingTime from './WorkingTime';
import './Dashboard.css'; // Optional: Import a CSS file for styling

const Dashboard = () => {
    return (
        <div className="dashboard">
            <h2 className="dashboard-title">Dashboard</h2>
            <div className="dashboard-content">
                <RecentActivities />
                <Projects />
                <WorkingTime />
            </div>
        </div>
    );
};

export default Dashboard;