//init varibles with default values lets there are issues reading them from config
let global_brightness = 0.5
let global_whiteBalanceFactors = {
    "red": 1.0,
    "green": 0.8,
    "blue": 0.6
}
let global_gamma = 2.2
const brightnessScaler = 100;


function setColorGlobals(shiftLightConfig) {
    whiteBalance_factors = shiftLightConfig.whiteBalance_factors
    gamma = shiftLightConfig.gamma
    brightness = shiftLightConfig.brightness
}

// Helper function to convert RGB color to HEX
function rgbToHex(rgb) {
    const result = rgb.match(/\d+/g).map(Number);
    return `#${((1 << 24) + (result[0] << 16) + (result[1] << 8) + result[2]).toString(16).slice(1).toUpperCase()}`;
}

function hexToRgb(hex) {
    hex = hex.replace(/^#/, "");
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);
    return { "red": r, "green": g, "blue": b };
}

function rgbToHsv(r, g, b) {
    r /= 255, g /= 255, b /= 255;
    let max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, v = max;
    let d = max - min;
    s = max === 0 ? 0 : d / max;

    if (max === min) {
        h = 0;
    } else if (max === r) {
        h = (60 * ((g - b) / d) + 360) % 360;
    } else if (max === g) {
        h = (60 * ((b - r) / d) + 120) % 360;
    } else {
        h = (60 * ((r - g) / d) + 240) % 360;
    }

    return { h, s, v };
}

function hsvToRgb(h, s, v) {
    h = h % 360;
    let c = v * s;
    let x = c * (1 - Math.abs((h / 60) % 2 - 1));
    let m = v - c;
    let r, g, b;

    if (0 <= h && h < 60) {
        r = c, g = x, b = 0;
    } else if (60 <= h && h < 120) {
        r = x, g = c, b = 0;
    } else if (120 <= h && h < 180) {
        r = 0, g = c, b = x;
    } else if (180 <= h && h < 240) {
        r = 0, g = x, b = c;
    } else if (240 <= h && h < 300) {
        r = x, g = 0, b = c;
    } else {
        r = c, g = 0, b = x;
    }

    return {
        red: Math.round((r + m) * 255),
        green: Math.round((g + m) * 255),
        blue: Math.round((b + m) * 255)
    };
}

function rgbStringToObject(rgbString) {
    const match = rgbString.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match) {
        throw new Error("Invalid RGB string format: " + rgbString);
    }
    return {
        red: parseInt(match[1]),
        green: parseInt(match[2]),
        blue: parseInt(match[3])
    };
}

function applyColorAdjustments(color, brightness = global_brightness, gamma = global_gamma, colorFactors = global_whiteBalanceFactors) {
    // Step 1: Apply brightness adjustment
    let { h, s, v } = rgbToHsv(color.red, color.green, color.blue);
    v *= brightness;
    let adjustedColor = hsvToRgb(h, s, v);

    // Step 2: Apply gamma correction
    adjustedColor = {
        red: Math.round(255 * Math.pow(adjustedColor.red / 255, gamma)),
        green: Math.round(255 * Math.pow(adjustedColor.green / 255, gamma)),
        blue: Math.round(255 * Math.pow(adjustedColor.blue / 255, gamma))
    };

    // Step 3: Apply white balance adjustment
    return {
        red: Math.round(adjustedColor.red * colorFactors.red),
        green: Math.round(adjustedColor.green * colorFactors.green),
        blue: Math.round(adjustedColor.blue * colorFactors.blue)
    };
}

function reverseColorAdjustments(color, brightness = global_brightness, gamma = global_gamma, colorFactors = global_whiteBalanceFactors) {
    // Step 1: Reverse white balance adjustment
    let corrected = {
        red: color.red / colorFactors.red,
        green: color.green / colorFactors.green,
        blue: color.blue / colorFactors.blue
    };

    // Step 2: Reverse gamma correction
    corrected = {
        red: Math.pow(corrected.red / 255, 1 / gamma) * 255,
        green: Math.pow(corrected.green / 255, 1 / gamma) * 255,
        blue: Math.pow(corrected.blue / 255, 1 / gamma) * 255
    };

    // Step 3: Reverse brightness adjustment
    let { h, s, v } = rgbToHsv(corrected.red, corrected.green, corrected.blue);
    v /= brightness;
    return hsvToRgb(h, s, v);
}
