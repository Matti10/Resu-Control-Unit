let selectedCircle = null;

const limiterScaler = 0.001
const colorContainers = document.querySelectorAll('[class="color-container"]');
const toggleSwitches = document.querySelectorAll('[class="toggleSwitch"]');
const pinSelectors = document.querySelectorAll('.pinSelector-dropdown');

let config = getAllConfig()

async function getAllConfig() {
    getEndpoint("/config")
    .then(config => {
        return config;
    })
}


async function getEndpoint(endpoint) {
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching config:', error);
        return null;
    }
}

function getLocalConfigFromEndpoint(endpoint) {
    endpoint = endpoint.replace("/config", "")
    const keys = endpoint.split('/').filter(key => key); // Split the path and filter out empty strings
    let value = config;

    for (const key of keys) {
        if (value[key] !== undefined) {
            value = value[key];
        } else {
            return undefined; // Return undefined if the key does not exist
        }
    }

    return value
}

async function setEndpoint(endpoint, data) {

    await fetch(`endpoint`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "data": data })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to update ${endpoint} with data: ${data} Error: ${response.statusText}`);
            }
            return response;
        })
        .then(data => console.log(`Updated ${endpoint} with data: ${data}`))
        .catch(error => console.error(error));
}

function setInnerTextFromEndpoint(element) {
    element.innerText = getLocalEndpoint(element.endpoint)
}



function downloadConfig() {
    window.location.href = '/downloadConfig';
}

function uploadConfig(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/uploadConfig', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('File uploaded successfully');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('File upload failed');
        });
}


function pickColor(circle) {
    selectedCircle = circle;  // Store the clicked circle

    // Get the position of the clicked circle on the screen
    const rect = circle.getBoundingClientRect();

    // Get the color picker element
    const colorPicker = document.getElementById('colorPicker');

    // Position the color picker at the clicked circle's location
    colorPicker.style.left = `${rect.left}px`;  // X position
    colorPicker.style.top = `${rect.top + rect.height + 10}px`;  // Y position (10px below the circle)

    // Set the color picker's value to the background color of the circle
    const bgColor = window.getComputedStyle(circle).backgroundColor;
    colorPicker.value = rgbToHex(bgColor);

    // Show the color picker before triggering the click event
    colorPicker.style.display = 'block';

    // Trigger a click event to show the color picker
    colorPicker.click();
}

function postColorChange(endpoint, id, newColor) {
    // Prepare the request payload
    const requestBody = {
        color: applyColorAdjustments(hexToRgb(newColor)) //apply color adjustments before sending to the server. 
    };

    setEndpoint(`${endpoint}/[${id}]/color`, requestBody)
}

function changeColor(event) {
    // Change the circle's background color
    let newColor = event.target.value;
    selectedCircle.style.backgroundColor = newColor;

    postColorChange(selectedCircle.endpoint, selectedCircle.id, newColor)
}

function addCirle(container, color, id) {
    const circle = document.createElement('div');
    circle.className = 'circle';
    circle.id = `${id}`;
    circle.endpoint = `/ShiftLights/ShiftLights/colors/[${id}`
    circle.onclick = function () { pickColor(this); };

    // Convert color values to CSS format
    circle.style.backgroundColor = `rgb(${color.red}, ${color.green}, ${color.blue})`;

    container.appendChild(circle);  // Append to shiftColor-container
}

function populateButtonGroup(container, buttonData) {
    let selected = buttonData.selected
    buttonData.options.forEach(pattern => {
        const button = document.createElement('button');
        button.id = `${pattern}-${container.id}`;
        button.innerText = pattern;
        button.onclick = function () { handleButtonGroupClick(this); };

        if (pattern === selected) {
            button.className = "pure-button pure-button-active";
        } else {
            button.className = "pure-button";
        }
        container.appendChild(button);
    });
}

function handleButtonGroupClick(button) {

    let buttons = button.parentNode.querySelectorAll("button");
    let endpoint = button.parentNode.getAttribute('endpoint')

    // Remove active class from all buttons
    buttons.forEach(btn => btn.className = "pure-button");

    // Add active class to the clicked button  
    button.className = "pure-button pure-button-active";

    // Send API request with the selected button's ID
    setEndpoint(endpoint, button.innerText)

}


function buildSlider(container, value, callback = setEndpoint) {
    const slider = container.getElementsByClassName("sliderBar")[0];
    const inputBox = container.getElementsByClassName("value")[0];

    slider.value = value
    inputBox.value = value

    // Sync input box with slider
    slider.oninput = function () {
        callback(this.endpoint, this.value)
        inputBox.value = this.value;
    };

    // Sync slider with input box (with min/max validation)
    inputBox.oninput = function () {
        if (this.value < slider.min) this.value = slider.min;
        if (this.value > slider.max) this.value = slider.max;
        slider.value = this.value;
        callback(this.endpoint, this.value)
    };
}

function buildButtonGroupsFromEndpoint() {
    let buttonGroup = document.getElementsByClassName("pure-button-group")

    let buttonInfo = getLocalConfigFromEndpoint(buttonGroup.endpoint)

    populateButtonGroup(buttonGroup, buttonInfo)
}

function buildColorCirclesFromEndpoint() {
    for (let i = 0; i < colorContainers.length; i++) {
        getLocalConfigFromEndpoint(colorContainers[i].endpoint).forEach(light => {
            addCirle(colorContainers[i], reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
        });
    }
}

function buildToggleSwitchesFromEndpoint() {
    for (let i = 0; i < toggleSwitches.length; i++) {
        toggleSwitches[i].checked = getLocalConfigFromEndpoint();
        toggleSwitches[i].addEventListener("change", function () {

            // show/hide content
            table = this.closest("table")
            const rows = table.querySelectorAll("tr:not(:first-child)");
            rows.forEach(row => {
                row.style.display = this.checked ? "" : "none";
            });

            setEndpoint(this.endpoint, this.checked);
        })
    }
}

async function setBrightness(endpoint, brightness) {
    global_brightness = brightness;
    // Iterate over the found elements
    for (let i = 0; i < colorContainers.length; i++) {
        const brightenedColors = Array.from(colorContainers[i].getElementsByClassName('circle')).map(circle => {
            // Get the color of the circle
            const color = circle.style.backgroundColor;
            const id = circle.id;

            return {
                id: id,
                color: applyColorAdjustments(rgbStringToObject(color), brightness / brightnessScaler) // divide by brightnessScaler as brightness is stored as a float between 0 and 1 on server
            };
        });

        // Store the fetch promise
        await setEndpoint(colorContainers[i].endpoint, brightenedColors)
        if (i < 1) {
            setEndpoint(endpoint, brightness / brightnessScaler) // divide by brightnessScaler as brightness is stored as a float between 0 and 1 on server
        }
    }
}

async function setLimiterPeriod(endpoint, value) {
    await setEndpoint(endpoint, value * limiterScaler);
}

function buildPinSelectorsFromEndpoint() {
    pinSelectors.forEach(pinSelector => {
        // Clear existing options (if any)
        pinSelector.innerHTML = '';
        const pinFunction = pinSelector.getAttribute('function-Name');
        const allowedClass = pinSelector.getAttribute('allowed-class');

        // Create "unassigned" option
        const unassignedOption = document.createElement('option');
        unassignedOption.style.backgroundColor = 'grey';
        unassignedOption.innerText = `Unassigned`;
        pinSelector.appendChild(option);


        // default selection to unassigned
        unassignedOption.selected = true;

        Object.entries(data.Pins).forEach(([pinNumber, pinData]) => {
            // Only add options that are "allowed"
            if (pinData.class.includes(allowedClass)) {
                const option = document.createElement('option');
                option.value = pinNumber;  // Use pinNumber as the value

                if (pinData.function !== "" && pinData.function !== pinFunction) {
                    option.disabled = true;
                    option.style.backgroundColor = 'black';
                    option.innerText = `Pin ${pinNumber} (in use)`;  // Display pinNumber as text

                } else {
                    option.innerText = `Pin ${pinNumber} (${pinData.class})`;  // Display pinNumber as text

                    // Set the background color based on the class of the pin
                    switch (pinData.class) {
                        case 'IO':
                            option.style.backgroundColor = 'blue';
                            break;
                        case 'I':
                            option.style.backgroundColor = 'green';
                            break;
                    }

                }

                // overwrite the default selection if the pin is already assigned
                if (pinFunction === pinData.function) {
                    option.selected = true;
                    pinSelector.style.backgroundColor = option.style.backgroundColor;
                }

                pinSelector.appendChild(option);
            }
        });

        // Add event listener to change the background color of the selection box and make API call
        pinSelector.addEventListener('change', function () {
            const selectedOption = pinSelector.options[pinSelector.selectedIndex];
            pinSelector.style.backgroundColor = selectedOption.style.backgroundColor;
            setEndpoint(pinSelector.endpoint,selectedOption)
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    getAllConfig();
    setColorGlobals(config.ShiftLights); // set color modification parameters
    buildButtonGroupsFromEndpoint();
    buildColorCirclesFromEndpoint();

    buildSlider(document.getElementById("brightnessSlider"), config.ShiftLights.brightness * brightnessScaler, setBrightness);
    buildSlider(document.getElementById("limiterPeriodSlider"), config.ShiftLights.Limiter.period_s / limiterScaler, setLimiterPeriod);
    //initialise position of toggle switch
    document.getElementById("shiftLights-table").getElementsByClassName("toggleSwitch") = config.ShiftLights.activated;
});


function updateRPM() {
    fetch('/rpm')
        .then(response => response.json())
        .then(data => document.getElementById('currentRPM').innerText = data.rpm);
}