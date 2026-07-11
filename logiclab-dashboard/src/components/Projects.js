import React, { useEffect, useState } from 'react';

const Projects = () => {
    const [projects, setProjects] = useState([]);

    useEffect(() => {
        // Fetch project data from an API or a local source
        const fetchProjects = async () => {
            try {
                const response = await fetch('/api/projects'); // Replace with your API endpoint
                const data = await response.json();
                setProjects(data);
            } catch (error) {
                console.error('Error fetching projects:', error);
            }
        };

        fetchProjects();
    }, []);

    return (
        <div className="projects">
            <h2 className="text-xl font-semibold mb-4">Projects</h2>
            <ul className="space-y-2">
                {projects.map((project) => (
                    <li key={project.id} className="border p-4 rounded-lg shadow">
                        <h3 className="font-bold">{project.name}</h3>
                        <p>{project.description}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Projects;