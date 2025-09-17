-- Create initial departments
INSERT INTO departments (name, description, created_at) VALUES 
('IT Support', 'General IT support and helpdesk services', NOW()),
('Network Operations', 'Network infrastructure and connectivity management', NOW()),
('Security', 'Information security and compliance', NOW()),
('Database Administration', 'Database management and optimization', NOW()),
('Application Development', 'Software development and maintenance', NOW())
ON CONFLICT (name) DO NOTHING;

-- Display created departments
SELECT id, name, description FROM departments ORDER BY id;
