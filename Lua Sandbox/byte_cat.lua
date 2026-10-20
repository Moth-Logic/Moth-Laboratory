#!/usr/bin/env lua
-- byte_cat.lua
-- Byte Cat: a very small terminal companion.
-- Feed him, play with him, brush him, let him sleep. He will do the rest.
-- Run with: lua byte_cat.lua

math.randomseed(os.time())

local SAVE_VERSION = 1

local script_dir = ""
if arg and arg[0] then
    script_dir = arg[0]:match("^(.*[/\\])") or ""
end
local SAVE_PATH = script_dir .. "bytecat_save.txt"

local state

-- Small helpers

local function clamp(value, low, high)
    if value < low then return low end
    if value > high then return high end
    return value
end

local function read_line(prompt)
    io.write(prompt)
    io.flush()
    local line = io.read("*l")
    if line == nil then return nil end
    return line:match("^%s*(.-)%s*$")
end

local function bar(value)
    local filled = math.floor(clamp(value, 0, 100) / 5 + 0.5)
    if filled > 20 then filled = 20 end
    return string.rep("#", filled) .. string.rep("-", 20 - filled)
end

local function clean_name(raw)
    if raw == nil then return "Byte" end
    raw = raw:gsub("[%c=]", "")
    raw = raw:sub(1, 16)
    if raw == "" then return "Byte" end
    return raw
end

local function with_name(text)
    return (text:gsub("Byte", function() return state.name end))
end

local function plural(count, singular, plural_form)
    if count == 1 then return singular end
    return plural_form
end

-- The cat

local function new_state()
    return {
        name = "Byte",
        fullness = 70,
        energy = 85,
        cleanliness = 80,
        happiness = 75,
        health = 100,
        day = 1,
        hour = 9,
        total_hours = 0,
    }
end

local function mood()
    if state.health <= 30 then return "sick" end
    if state.fullness <= 20 then return "hungry" end
    if state.energy <= 20 then return "sleepy" end
    if state.cleanliness <= 20 then return "dirty" end
    if state.happiness <= 30 then return "sad" end
    if state.happiness >= 80 and state.fullness >= 50 then return "happy" end
    return "content"
end

local FACES = {
    happy = {
        "  /\\_/\\  ",
        " ( ^.^ ) ",
        "  > w <  ",
    },
    content = {
        "  /\\_/\\  ",
        " ( o.o ) ",
        "  > ^ <  ",
    },
    sad = {
        "  /\\_/\\  ",
        " ( ;.; ) ",
        "  > . <  ",
    },
    hungry = {
        "  /\\_/\\  ",
        " ( o.o ) ",
        "  > O <  ",
    },
    sleepy = {
        "  /\\_/\\  ",
        " ( -.- ) ",
        "  > ^ < zZ",
    },
    dirty = {
        "  /\\_/\\  ",
        " ( o.o ) ",
        "  > ^ < ~ ",
    },
    sick = {
        "  /\\_/\\  ",
        " ( x.x ) ",
        "  > ~ <  ",
    },
}

local function status_line()
    local name = state.name
    local current = mood()
    if current == "happy" then
        return name .. " is purring like a small engine."
    elseif current == "content" then
        return name .. " is loafing nearby, keeping an eye on you."
    elseif current == "sad" then
        return name .. " is curled up and quiet."
    elseif current == "hungry" then
        return name .. " keeps glancing at the food bowl."
    elseif current == "sleepy" then
        return name .. " is losing a fight with a yawn."
    elseif current == "dirty" then
        return name .. " looks like he rolled through a dust bunny."
    else
        return name .. " is looking rough. Food, a brush and rest should help."
    end
end

local function time_text()
    return string.format("Day %d, %02d:00", state.day, state.hour)
end

local function draw_screen()
    local face = FACES[mood()]
    local clock = time_text()
    local padding = 44 - #state.name - #clock
    if padding < 1 then padding = 1 end

    print("")
    print("  " .. state.name .. string.rep(" ", padding) .. clock)
    print("  " .. string.rep("-", 46))
    for _, line in ipairs(face) do
        print("  " .. line)
    end
    print("  " .. string.rep("-", 46))
    print(string.format("  %-8s[%s] %3d", "Belly", bar(state.fullness), math.floor(state.fullness)))
    print(string.format("  %-8s[%s] %3d", "Energy", bar(state.energy), math.floor(state.energy)))
    print(string.format("  %-8s[%s] %3d", "Clean", bar(state.cleanliness), math.floor(state.cleanliness)))
    print(string.format("  %-8s[%s] %3d", "Happy", bar(state.happiness), math.floor(state.happiness)))
    print(string.format("  %-8s[%s] %3d", "Health", bar(state.health), math.floor(state.health)))
    print("")
    print("  " .. status_line())
    print("")
    print("  [1] Feed   [2] Play   [3] Pet   [4] Clean")
    print("  [5] Sleep  [6] Check  [7] Help  [8] Quit")
end

-- Health and time

local function update_health()
    if state.fullness <= 15 or state.cleanliness <= 15 then
        state.health = state.health - 4
    elseif state.happiness <= 20 or state.energy <= 10 then
        state.health = state.health - 2
    elseif state.fullness >= 55 and state.cleanliness >= 55
        and state.happiness >= 60 and state.energy >= 30 then
        state.health = state.health + 2
    end
    state.health = clamp(state.health, 0, 100)
end

local function pass_time(hours, sleeping)
    state.hour = state.hour + hours
    while state.hour >= 24 do
        state.hour = state.hour - 24
        state.day = state.day + 1
    end
    state.total_hours = state.total_hours + hours

    local fullness_rate = sleeping and 2 or 4
    state.fullness = clamp(state.fullness - fullness_rate * hours, 0, 100)

    if sleeping then
        state.cleanliness = clamp(state.cleanliness - 1.5 * hours, 0, 100)
        state.happiness = clamp(state.happiness + 1 * hours, 0, 100)
    else
        state.energy = clamp(state.energy - 3 * hours, 0, 100)
        state.cleanliness = clamp(state.cleanliness - 2 * hours, 0, 100)
        state.happiness = clamp(state.happiness - 1.5 * hours, 0, 100)
    end

    update_health()
end

-- Little things that happen on their own

local EVENTS = {
    {
        text = "A moth taps the window. Byte chases it for a solid minute.",
        happiness = 6,
    },
    {
        text = "Byte coughs up a hairball on your notes, then looks proud.",
        cleanliness = -7,
        happiness = 2,
    },
    {
        text = "Byte finds a sunbeam and melts into it.",
        energy = 6,
        happiness = 3,
    },
    {
        text = "Byte knocks a pen off the desk and watches it fall.",
        happiness = 4,
    },
    {
        text = "A tiny zoomie happens. A chair is slightly moved.",
        energy = -5,
        happiness = 8,
    },
    {
        text = "Byte grooms a paw with enormous seriousness.",
        cleanliness = 5,
    },
    {
        text = "You get a slow blink. That is cat for 'I love you.'",
        happiness = 5,
    },
}

local DREAMS = {
    "Byte dreams of a fish the size of a sofa.",
    "Byte dreams he is a tiger. The desk does not agree.",
    "Byte dreams of a warm laundry basket with no bottom.",
    "Byte dreams of catching the red dot. Finally.",
    "Byte dreams of a world where the food bowl refills itself.",
}

local function maybe_event()
    if math.random() < 0.22 then
        local event = EVENTS[math.random(#EVENTS)]
        state.fullness = clamp(state.fullness + (event.fullness or 0), 0, 100)
        state.energy = clamp(state.energy + (event.energy or 0), 0, 100)
        state.cleanliness = clamp(state.cleanliness + (event.cleanliness or 0), 0, 100)
        state.happiness = clamp(state.happiness + (event.happiness or 0), 0, 100)
        print("  " .. with_name(event.text))
    end
end


-- Actions

local FOODS = {
    {
        name = "Kibble",
        description = "the reliable option",
        fullness = 26,
        happiness = 0,
        health = 0,
        text = "Crunch, crunch. Byte approves of the classics.",
    },
    {
        name = "Tuna",
        description = "the good stuff",
        fullness = 38,
        happiness = 6,
        health = 1,
        text = "Byte inhales the tuna and looks at you like you owe him another.",
    },
    {
        name = "Milk",
        description = "a little treat",
        fullness = 18,
        happiness = 4,
        health = 0,
        text = "Byte laps up the milk, then sneezes dramatically.",
    },
    {
        name = "Cookie",
        description = "not technically cat food",
        fullness = 8,
        happiness = 14,
        health = -4,
        text = "Byte devours the cookie. The sugar rush is imminent.",
    },
}

local TOYS = {
    "a crumpled receipt",
    "the red dot",
    "a bottle cap",
    "a piece of string",
    "an imaginary mouse",
}

local function feed()
    print("")
    print("  What is for dinner?")
    for index, food in ipairs(FOODS) do
        print(string.format("    %d. %-7s %s", index, food.name, food.description))
    end
    print("    0. Never mind")

    local choice = read_line("  Food: ")
    local index = tonumber(choice)
    if not index or index == 0 then
        print("  " .. state.name .. " headbutts the empty bowl anyway.")
        return
    end

    local food = FOODS[index]
    if not food then
        print("  " .. state.name .. " stares at you. That was not on the menu.")
        return
    end

    if state.fullness >= 95 then
        print("  " .. state.name .. " is already round enough. He gives the bowl a polite sniff.")
        return
    end

    print("")
    state.fullness = clamp(state.fullness + food.fullness, 0, 100)
    state.happiness = clamp(state.happiness + food.happiness, 0, 100)
    state.health = clamp(state.health + food.health, 0, 100)
    pass_time(1)
    print("  " .. with_name(food.text))
    maybe_event()
end

local function play()
    if state.energy < 15 then
        print("")
        print("  " .. state.name .. " flops over dramatically. He is too tired to play right now.")
        return
    end

    local toy = TOYS[math.random(#TOYS)]
    state.energy = clamp(state.energy - 14, 0, 100)
    state.happiness = clamp(state.happiness + 20, 0, 100)
    state.cleanliness = clamp(state.cleanliness - 6, 0, 100)
    pass_time(2)

    print("")
    print("  You and " .. state.name .. " play with " .. toy .. " for a while.")
    print("  " .. state.name .. " takes the game very seriously. You lose.")
    maybe_event()
end

local function pet()
    state.happiness = clamp(state.happiness + 10, 0, 100)
    pass_time(1)
    print("")
    print("  " .. state.name .. " leans into your hand, then pretends he did not.")
    maybe_event()
end

local function clean()
    if state.cleanliness >= 95 then
        print("")
        print("  " .. state.name .. " is already spotless and deeply offended by the brush.")
        return
    end

    state.cleanliness = clamp(state.cleanliness + 35, 0, 100)
    state.happiness = clamp(state.happiness - 3, 0, 100)
    pass_time(1)

    print("")
    print("  You brush " .. state.name .. " until he sparkles. He acts like this was his idea.")
    maybe_event()
end

local function sleep()
    if state.fullness < 35 then
        print("")
        print("  " .. state.name .. " paces by the empty bowl. He needs a proper meal before sleeping.")
        return
    end

    local dream = DREAMS[math.random(#DREAMS)]
    state.energy = 100
    pass_time(8, true)
    state.health = clamp(state.health + 4, 0, 100)

    print("")
    print("  " .. state.name .. " curls into a comma and sleeps for eight hours.")
    print("  Dream: " .. with_name(dream))
    print("  He wakes up, yawns, and expects breakfast.")
end

local function describe(value)
    if value >= 80 then return "great" end
    if value >= 45 then return "fine" end
    if value >= 25 then return "not great" end
    return "bad"
end

local function check()
    print("")
    print("  " .. state.name .. ", a closer look")
    print("  Belly:  " .. math.floor(state.fullness) .. "/100 (" .. describe(state.fullness) .. ")")
    print("  Energy: " .. math.floor(state.energy) .. "/100 (" .. describe(state.energy) .. ")")
    print("  Clean:  " .. math.floor(state.cleanliness) .. "/100 (" .. describe(state.cleanliness) .. ")")
    print("  Happy:  " .. math.floor(state.happiness) .. "/100 (" .. describe(state.happiness) .. ")")
    print("  Health: " .. math.floor(state.health) .. "/100 (" .. describe(state.health) .. ")")
    print("")

    local tips = {}
    if state.fullness < 45 then tips[#tips + 1] = "Some tuna would not go amiss." end
    if state.energy < 30 then tips[#tips + 1] = "He could use a nap." end
    if state.cleanliness < 35 then tips[#tips + 1] = "The brush is right there." end
    if state.happiness < 35 then tips[#tips + 1] = "A little playtime would help." end
    if #tips == 0 then
        tips[1] = "Honestly? He is doing great. Keep doing whatever you are doing."
    end
    for _, tip in ipairs(tips) do
        print("  " .. tip)
    end

    local days = math.floor(state.total_hours / 24)
    print("")
    print("  Time together: " .. days .. " " .. plural(days, "day", "days")
        .. ", " .. (state.total_hours % 24) .. " " .. plural(state.total_hours % 24, "hour", "hours"))
    print("  Save file: " .. SAVE_PATH)
end

local function help()
    print("")
    print("  Byte Cat, the short version")
    print("  ----------------------------")
    print("  Feed   fill his belly. Tuna is the favourite.")
    print("  Play   spend energy to make him happy.")
    print("  Pet    free affection, small happiness boost.")
    print("  Clean  brush off the dust. He tolerates it.")
    print("  Sleep  eight hours, full energy. Do not skip meals.")
    print("  Check  exact stats and a blunt assessment.")
    print("  Quit   saves the game and lets Byte nap.")
    print("")
    print("  Type a number or the action name. Every action moves time forward.")
    print("  If his health hits zero, that is the end of this life.")
    print("  Delete bytecat_save.txt (next to this script) to start over.")
end

local ACTIONS = {
    ["1"] = feed,
    ["feed"] = feed,
    ["2"] = play,
    ["play"] = play,
    ["3"] = pet,
    ["pet"] = pet,
    ["4"] = clean,
    ["clean"] = clean,
    ["5"] = sleep,
    ["sleep"] = sleep,
    ["6"] = check,
    ["check"] = check,
    ["status"] = check,
    ["7"] = help,
    ["help"] = help,
}

-- Saving


local SAVE_FIELDS = {
    "name", "fullness", "energy", "cleanliness", "happiness", "health",
    "day", "hour", "total_hours",
}

local function save_game()
    local file = io.open(SAVE_PATH, "w")
    if not file then return false end

    file:write("version=" .. SAVE_VERSION .. "\n")
    for _, key in ipairs(SAVE_FIELDS) do
        local value = state[key]
        if type(value) == "string" then
            value = value:gsub("[\r\n=]", " ")
        end
        file:write(key .. "=" .. tostring(value) .. "\n")
    end
    file:close()
    return true
end

local function load_game()
    local file = io.open(SAVE_PATH, "r")
    if not file then return nil end

    local data = {}
    for line in file:lines() do
        local key, value = line:match("^([%w_]+)=(.*)$")
        if key then data[key] = value end
    end
    file:close()

    if tonumber(data.version) ~= SAVE_VERSION then return nil end

    local loaded = new_state()
    loaded.name = clean_name(data.name)

    local numeric = {
        "fullness", "energy", "cleanliness", "happiness", "health",
        "day", "hour", "total_hours",
    }
    for _, key in ipairs(numeric) do
        local value = tonumber(data[key])
        if value == nil then return nil end
        loaded[key] = value
    end

    loaded.fullness = clamp(loaded.fullness, 0, 100)
    loaded.energy = clamp(loaded.energy, 0, 100)
    loaded.cleanliness = clamp(loaded.cleanliness, 0, 100)
    loaded.happiness = clamp(loaded.happiness, 0, 100)
    loaded.health = clamp(loaded.health, 0, 100)
    loaded.day = math.max(1, math.floor(loaded.day))
    loaded.hour = math.floor(loaded.hour) % 24
    loaded.total_hours = math.max(0, math.floor(loaded.total_hours))

    return loaded
end

-- ---------------------------------------------------------------------------
-- Game flow
-- ---------------------------------------------------------------------------

local function print_title()
    print("")
    print("   ____        _         ____      _   ")
    print("  | __ ) _   _| |_ ___  / ___|__ _| |_ ")
    print("  |  _ \\| | | | __/ _ \\| |   / _` | __|")
    print("  | |_) | |_| | ||  __/| |__| (_| | |_ ")
    print("  |____/ \\__, |\\__\\___| \\____\\__,_|\\__|")
    print("         |___/                        ")
    print("  a very small terminal companion")
end

local function game_over()
    print("")
    print("  " .. state.name .. " curls up in his box one last time.")
    print("  The food bowl is still half full. The sunbeam has moved on.")
    print("")
    print("  You gave him " .. math.floor(state.total_hours / 24) .. " "
        .. plural(math.floor(state.total_hours / 24), "day", "days")
        .. " and " .. (state.total_hours % 24) .. " "
        .. plural(state.total_hours % 24, "hour", "hours") .. ".")
    print("  Somewhere, a red dot is still moving.")
    os.remove(SAVE_PATH)
end

local function game_loop()
    while true do
        draw_screen()
        local choice = read_line("  > ")

        if choice == nil then
            save_game()
            print("")
            print("  " .. state.name .. " watches you go. (Game saved.)")
            return "quit"
        end

        local command = choice:lower()
        if command == "8" or command == "q" or command == "quit" or command == "exit" then
            save_game()
            print("")
            print("  " .. state.name .. " curls up by the door. See you tomorrow.")
            return "quit"
        end

        local action = ACTIONS[command]
        if action then
            action()
        else
            print("")
            print("  " .. state.name .. " tilts his head. Try a number from 1 to 8, or type 'help'.")
        end

        if state.health <= 0 then
            return "dead"
        end

        save_game()
    end
end

local function run()
    print_title()

    local loaded = load_game()
    if loaded then
        state = loaded
        print("")
        print("  " .. state.name .. " blinks awake the moment you sit down.")
    else
        state = new_state()
        print("")
        print("  A small cardboard box sits on your desk.")
        print("  Something inside sneezes.")
        print("  What should we call your cat? (Byte)")
        local name = read_line("  Name: ")
        if name == nil then
            print("")
            print("  You leave the box unopened. Maybe tomorrow.")
            return
        end
        state.name = clean_name(name)
        print("")
        print("  " .. state.name .. " climbs out, judges your desk, and approves.")
        save_game()
    end

    while true do
        local result = game_loop()
        if result == "quit" then return end

        game_over()
        print("  Take home another kitten? (y/n)")
        local again = read_line("  > ")
        if again == nil then return end
        if again:lower():sub(1, 1) ~= "y" then
            print("")
            print("  The box stays empty for now.")
            return
        end

        state = new_state()
        print("")
        print("  A new tiny cat immediately sits on your keyboard.")
        print("  Name? (Byte)")
        local name = read_line("  Name: ")
        if name == nil then return end
        state.name = clean_name(name)
        save_game()
    end
end

run()
