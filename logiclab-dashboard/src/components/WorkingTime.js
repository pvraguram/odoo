import React from 'react';

const WorkingTime = () => {
    // Sample data for working time statistics
    const workingTimeData = {
        totalHours: 40,
        totalProjects: 5,
        averageDailyHours: 8,
    };

    return (
        <div className="working-time">
            <h2 className="text-xl font-semibold mb-4">Working Time Statistics</h2>
            <div className="stats">
                <div className="stat-item">
                    <h3 className="text-lg">Total Working Hours</h3>
                    <p className="text-2xl font-bold">{workingTimeData.totalHours} hours</p>
                </div>
                <div className="stat-item">
                    <h3 className="text-lg">Total Projects</h3>
                    <p className="text-2xl font-bold">{workingTimeData.totalProjects}</p>
                </div>
                <div className="stat-item">
                    <h3 className="text-lg">Average Daily Hours</h3>
                    <p className="text-2xl font-bold">{workingTimeData.averageDailyHours} hours</p>
                </div>
            </div>
        </div>
    );
};

export default WorkingTime;