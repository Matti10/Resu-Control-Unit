//This should be a class
//init varibles with default values lets there are issues reading them from config
let global_brightness = 0.5
let global_whiteBalanceFactors = {
    "r": 1.0,
    "g": 0.8,
    "b": 0.6
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
    return { "r": r, "g": g, "b": b };
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
        r: Math.round((r + m) * 255),
        g: Math.round((g + m) * 255),
        b: Math.round((b + m) * 255)
    };
}

function rgbStringToObject(rgbString) {
    const match = rgbString.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match) {
        throw new Error("Invalid RGB string format: " + rgbString);
    }
    return {
        r: parseInt(match[1]),
        g: parseInt(match[2]),
        b: parseInt(match[3])
    };
}

function applyColorAdjustments(color, brightness = global_brightness, gamma = global_gamma, colorFactors = global_whiteBalanceFactors) {
    // Step 1: Apply brightness adjustment
    let { h, s, v } = rgbToHsv(color.r, color.g, color.b);
    v *= brightness;
    let adjustedColor = hsvToRgb(h, s, v);

    // Step 2: Apply gamma correction
    adjustedColor = {
        r: Math.round(255 * Math.pow(adjustedColor.r / 255, gamma)),
        g: Math.round(255 * Math.pow(adjustedColor.g / 255, gamma)),
        b: Math.round(255 * Math.pow(adjustedColor.b / 255, gamma))
    };

    // Step 3: Apply white balance adjustment
    return {
        r: Math.round(adjustedColor.r * colorFactors.r),
        g: Math.round(adjustedColor.g * colorFactors.g),
        b: Math.round(adjustedColor.b * colorFactors.b)
    };
}

function reverseColorAdjustments(color, brightness = global_brightness, gamma = global_gamma, colorFactors = global_whiteBalanceFactors) {
    // Step 1: Reverse white balance adjustment
    let corrected = {
        r: color.r / colorFactors.r,
        g: color.g / colorFactors.g,
        b: color.b / colorFactors.b
    };

    // Step 2: Reverse gamma correction
    corrected = {
        r: Math.pow(corrected.r / 255, 1 / gamma) * 255,
        g: Math.pow(corrected.g / 255, 1 / gamma) * 255,
        b: Math.pow(corrected.b / 255, 1 / gamma) * 255
    };

    // Step 3: Reverse brightness adjustment
    let { h, s, v } = rgbToHsv(corrected.r, corrected.g, corrected.b);
    v /= brightness;
    return hsvToRgb(h, s, v);
}
