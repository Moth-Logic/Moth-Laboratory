-- Simple Lua practice skeleton

-- Variables
name = "Lua learner"
age = 18
score = 0

-- Function: greet the player
local function greet(player_name)
    print("Hello, " .. player_name .. "!")
end

-- Function: add points to the score
local function add_score(points)
    score = score + points
    print("Current score: " .. score)
end

-- Main program
print("Welcome to your Lua practice file!")
greet(name)
print("Age:", age)
add_score(5)
add_score(10)

-- Example of a loop
for i = 1, 3 do
    print("Loop count:", i)
end

-- Example of an if statement
if score >= 10 then
    print("You reached a good score!")
else
    print("Keep practicing!")
end

-- Bonus: small table example
inventory = { "sword", "shield", "potion" }
print("First item:", inventory[1])

-- Try these ideas:
-- 1. Make a function to multiply two numbers
-- 2. Create a table with player stats
-- 3. Use a while loop
-- 4. Add a small game menu
