import express, { Request, Response } from "express";
import User from "../models/user";
import bcrypt from "bcrypt";
import crypto from "crypto";

const router = express.Router();

// POST route for /api/register
router.post("/register", async (req: Request, res: Response) => {
  const { name, username, email, password, appliedSettings } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: "Missing information!" });
  }

  try {
    const usernameExists = await checkUsernameExists(username);
    if (usernameExists) {
      return res.status(400).json({ message: "Username already exists" });
    }

    const emailExists = await checkEmailExists(email);
    if (emailExists) {
      return res.status(400).json({ message: "Email already exists" });
    }

    const userCount = await countUsers();
    const newID = userCount + 1;

    const pepper = process.env["PEPPER"] as string;

    // Function to generate HMAC-SHA256 hash
    function generateHMAC(password: string, pepper: string) {
      const hmac = crypto.createHmac("sha256", pepper);
      hmac.update(password);
      return hmac.digest("base64");
    }

    // Modify password hashing (add pepper)
    const passwordHMAC = generateHMAC(password, pepper);

    // Hash the password
    const saltRounds = 10;
    const passwordHash = await bcrypt
      .hash(passwordHMAC, saltRounds)
      .then((hash) => {
        return hash;
      })
      .catch((err) => {
        throw new Error(err.message);
      });

    const newUser = new User({
      id: newID,
      name: name,
      username: username,
      email: email,
      password: passwordHash,
      favouriteMenus: [],
      favouriteMensas: {
        archimedes: false,
        clausiusbar: false,
        dozentenfoyer: false,
        "food-lab": false,
        "mensa-polyterrasse-lunch": false,
        "mensa-polyterrasse-dinner": false,
        polysnack: false,
        tannenbar: false,
        "alumni-quattro-lounge-lunch": false,
        "alumni-quattro-lounge-dinner": false,
        "bistro-hpi": false,
        "food-market-green-day": false,
        "food-market-grill-bbq": false,
        "food-market-pizza-pasta-day": false,
        "food-market-dinner": false,
        "fusion-meal": false,
        "fusion-coffee": false,
        "rice-up": false,
        octavo: false,
        "uzh-untere-mensa-lunch": false,
        "uzh-untere-mensa-dinner": false,
        "uzh-obere-mensa": false,
        "lichthof-rondell": false,
        "raemi-59": false,
        "platte-14": false,
        "uzh-irchel": false,
        "cafeteria-irchel-seerose-lunch": false,
        "cafeteria-irchel-seerose-dinner": false,
        binzmuehle: false,
        "cafeteria-cityport": false,
        "cafeteria-zentrum-fuer-zahnmedizin": false,
        "cafeteria-tierspital": false,
        "cafeteria-botanischer-garten": false,
      },
      appliedSettings: appliedSettings,
    });

    await newUser.save();
    return res.status(200).json({ message: "Successfully registered!" });
  } catch (error) {
    console.error("Error registering user:", error);
    return res.status(500).json({ message: "Internal Server Error" });
  }
});

// POST route for /api/authenticate
router.post("/authenticate", async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: "Username and password required!" });
  }

  try {
    const existingUser = await User.findOne({ username });

    if (!existingUser) {
      return res.status(401).json({ message: "Wrong username or password" });
    }

    const pepper = process.env["PEPPER"] as string;

    // Function to generate HMAC-SHA256 hash
    function generateHMAC(password: string, pepper: string) {
      const hmac = crypto.createHmac("sha256", pepper);
      hmac.update(password);
      return hmac.digest("base64");
    }

    // Modify password hashing (add pepper)
    const passwordHMAC = generateHMAC(password, pepper);

    const passwordMatch = await bcrypt.compare(
      passwordHMAC,
      existingUser.password
    );

    if (passwordMatch) {
      req.session.userId = existingUser.id;
      req.session.appliedSettings = existingUser.appliedSettings;
      return res.status(200).json({ message: "Authentication successful!" });
    } else {
      return res.status(401).json({ message: "Wrong username or password" });
    }
  } catch (error) {
    console.error("Error authenticating user:", error);
    return res.status(500).json({ message: "Internal Server Error" });
  }
});

// POST route for /api/logout
router.post("/logout", (req, res) => {
  req.session.userId = -1;
  req.session.destroy((err) => {
    if (err) {
      console.error("Error logging out:", err);
      return res.status(500).json({ message: "Internal Server Error" });
    }

    return res.status(200).json({ message: "Logout successful!" });
  });
});

async function checkUsernameExists(usernameToCheck: string) {
  try {
    const existingUser = await User.findOne({ username: usernameToCheck });

    if (existingUser) {
      return true;
    } else {
      return false;
    }
  } catch (error) {
    console.error("Error checking username:", error);
    throw new Error("Error checking username");
  }
}

async function checkEmailExists(emailToCheck: string) {
  try {
    const existingUser = await User.findOne({ email: emailToCheck });

    if (existingUser) {
      return true;
    } else {
      return false;
    }
  } catch (error) {
    console.error("Error checking email:", error);
    throw new Error("Error checking email");
  }
}

async function countUsers() {
  try {
    const userCount = await User.countDocuments();
    return userCount;
  } catch (error) {
    console.error("Error counting users:", error);
    throw new Error("Error counting users");
  }
}

export default router;
