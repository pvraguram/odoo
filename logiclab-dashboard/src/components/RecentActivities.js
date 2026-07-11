import React, { useEffect, useState } from 'react';

const RecentActivities = () => {
    const [activities, setActivities] = useState([]);

    useEffect(() => {
        // Fetch recent activities from an API or a local source
        const fetchActivities = async () => {
            // Replace with your API endpoint
            const response = await fetch('/api/recent-activities');
            const data = await response.json();
            setActivities(data);
        };

        fetchActivities();
    }, []);

    return (
        <div className="recent-activities">
            <h2 className="text-xl font-semibold mb-4">Recent Activities</h2>
            <ul className="activity-list">
                {activities.map((activity, index) => (
                    <li key={index} className="activity-item">
                        <span className="activity-time">{activity.time}</span>
                        <span className="activity-description">{activity.description}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default RecentActivities;