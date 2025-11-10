-- Create Database
CREATE DATABASE AIImageMaker;
GO

USE AIImageMaker;
GO

-- Create Users Table
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(100) NOT NULL UNIQUE,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    CreatedAt DATETIME DEFAULT GETDATE()
);
GO

-- Create ImageGenerations Table
CREATE TABLE ImageGenerations (
    ImageID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT FOREIGN KEY REFERENCES Users(UserID),
    Prompt NVARCHAR(MAX) NOT NULL,
    NegativePrompt NVARCHAR(MAX),
    ImagePath NVARCHAR(500) NOT NULL,
    ModelUsed NVARCHAR(200),
    GeneratedAt DATETIME DEFAULT GETDATE(),
    Width INT DEFAULT 512,
    Height INT DEFAULT 512,
    Steps INT DEFAULT 50
);
GO

-- Create Index for better query performance
CREATE INDEX idx_user_images ON ImageGenerations(UserID);
CREATE INDEX idx_generated_date ON ImageGenerations(GeneratedAt DESC);
GO

-- Insert Sample User
INSERT INTO Users (Username, Email) 
VALUES ('demo_user', 'demo@example.com');
GO

-- View to see all generations with user info
CREATE VIEW vw_ImageGenerations AS
SELECT 
    ig.ImageID,
    ig.Prompt,
    ig.NegativePrompt,
    ig.ImagePath,
    ig.Width,
    ig.Height,
    ig.Steps,
    ig.GeneratedAt,
    ig.ModelUsed,
    u.Username,
    u.Email
FROM ImageGenerations ig
INNER JOIN Users u ON ig.UserID = u.UserID;
GO



-- after generate testing queries

USE AIImageMaker;
GO

-- Check all generated images
SELECT * FROM ImageGenerations ORDER BY GeneratedAt DESC;

-- Check image count
SELECT COUNT(*) as TotalImages FROM ImageGenerations;

-- View images with user details
SELECT 
    ig.ImageID,
    ig.Prompt,
    ig.ImagePath,
    ig.Width,
    ig.Height,
    ig.Steps,
    ig.GeneratedAt,
    u.Username
FROM ImageGenerations ig
JOIN Users u ON ig.UserID = u.UserID
ORDER BY ig.GeneratedAt DESC;

-- Get latest 5 generations
SELECT TOP 5
    ImageID,
    LEFT(Prompt, 50) + '...' as ShortPrompt,
    ImagePath,
    GeneratedAt
FROM ImageGenerations
ORDER BY GeneratedAt DESC;