let selectedCircle = null;

const limiterScaler = 0.001
let config = getAllConfig()

async function getAllConfig() {
    const config = await getConfigEndpoint("/config");
    return config;
}


async function getConfigEndpoint(endpoint) {
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
    endpoint = endpoint.replace("/config","")
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

async function setConfigEndpoint(endpoint,data) {
        
        await fetch(`endpoint`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
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
    element.innerText = getConfigEndpoint(element.endpoint)
}

function setConfigFromEndpoint(element, data) {
    setConfigEndpoint(element.endpoint,data)
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

    setConfigEndpoint(`${endpoint}/[${id}]/color`, requestBody)
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
    fetch(`${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ pattern: button.innerText })
    }).catch(error => console.error("Error sending API request:", error));
}


function buildSlider(container,value,callback) {
    const slider = container.getElementsByClassName("sliderBar")[0];
    const inputBox = container.getElementsByClassName("value")[0];

    slider.value = value 
    inputBox.value = value 

    // Sync input box with slider
    slider.oninput = function () {
        callback(this.value)
        inputBox.value = this.value;
    };

    // Sync slider with input box (with min/max validation)
    inputBox.oninput = function () {
        if (this.value < slider.min) this.value = slider.min;
        if (this.value > slider.max) this.value = slider.max;
        slider.value = this.value;
        callback(this.value)
    };
}

function buildButtonGroupFromEndpoint() {
    document.getElementsByClassName("")
}

function setLimiterPerid() {

}

async function setBrightness(brightness) {
    global_brightness = brightness;

    // Find all elements with class names that contain "Color-container"
    const colorContainers = document.querySelectorAll('[class*="Color-container"]');
    const brightenedColorsPromises = [];
    // TODO ONLY DO MATH ON SHIFTLIGHTS THEN SEND BRIGHTNESS UPDATE //TODO
    // Iterate over the found elements
    colorContainers.forEach(container => {
        const endpoint = container.getAttribute('endpoint');
        const brightenedColors = Array.from(container.getElementsByClassName('circle')).map(circle => {
            // Get the color of the circle
            const color = circle.style.backgroundColor;
            const id = circle.id;

            return {
                id: id,
                color: applyColorAdjustments(rgbStringToObject(color), brightness / brightnessScaler) // divide by brightnessScaler as brightness is stored as a float between 0 and 1 on server
            };
        });

        // Store the fetch promise
        brightenedColorsPromises.push(fetch(`/config${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ colors: brightenedColors })
        }).catch(error => console.error("Error sending API request:", error)));
    });

    // Wait for all fetch requests to complete
    await Promise.all(brightenedColorsPromises);

    // Send a single fetch request for brightness
    fetch("/ShiftLights/brightness", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ brightness: brightness / brightnessScaler }) // divide by brightnessScaler as brightness is stored as a float between 0 and 1 on server
    }).catch(error => console.error("Error sending API request:", error));
}

// function buildWhiteBalanceInputs()

document.addEventListener("DOMContentLoaded", () => {
    fetch('/config/RPMReader')
        .then(response => response.json())
        .then(data => {
            populateButtonGroup(document.querySelector('.rpmInput-containter'), data.readerModes);// rev pattern buttons
            
        });
    
    fetch('/config/ShiftLights')
        .then(response => response.json())
        .then(data => {
            setColorGlobals(data); // set color modification parameters

            // shift light circles
            data.ShiftLights.colors.forEach(light => {
                addCirle(document.querySelector('.shiftColor-container'), reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
            });

            // limiter circles
            data.Limiter.colors.forEach(light => {
                addCirle(document.querySelector('.limiterColor-container'), reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
            });

            // button groups
            populateButtonGroup(document.querySelector('.limiterPattern-containter'), data.Limiter.pattern);// limiter pattern buttons
            populateButtonGroup(document.querySelector('.revPattern-containter'), data.ShiftLights.pattern);// rev pattern buttons

            // brightness slider
            buildSlider(document.getElementById("brightnessSlider"),data.brightness*brightnessScaler,setBrightness);
            buildSlider(document.getElementById("limiterPeriodSlider"),data.Limiter.period_s/limiterScaler,setLimiterPerid);

            //initialise position of toggle switch
            document.getElementById("shiftLights-table").getElementsByClassName("toggleSwitch").checked = data.activated
        })
        .catch(error => console.error('Error fetching ShiftLights:', error));

    // pin Selection
    fetch('/config/Pins')
        .then(response => response.json())
        .then(data => {
            const pinSelectors = document.querySelectorAll('.pinSelector-dropdown');

            pinSelectors.forEach(pinSelector => {
                // Clear existing options (if any)
                pinSelector.innerHTML = '';
                const pinFunction = pinSelector.getAttribute('function-Name');
                const allowedClass = pinSelector.getAttribute('allowed-class');

                // Create "unassigned" option
                const option = document.createElement('option');
                option.style.backgroundColor = 'grey';
                option.innerText = `Unassigned`;  // Display pinNumber as text
                pinSelector.appendChild(option);


                // default selection to unassigned
                option.selected = true;

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

                    // Get the endpoint from the data attribute of the <select> element
                    const endpoint = pinSelector.getAttribute('endpoint');
                    const payload = {
                        selectedPin: selectedOption.value
                    };

                    fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Failed to update pin: ${response.statusText}`);
                            }
                            return response.json();
                        })
                        .then(data => console.log('Pin update successful:', data))
                        .catch(error => console.error('Error updating pin:', error));
                });
            });
        })
        .catch(error => console.error('Error fetching pins:', error));

    setInterval(updateRPM, 100); // Poll every 500ms

});

// Toggle switches for enabling/disabling functionality
Array.from(document.getElementsByClassName("toggleSwitch")).forEach(toggleSwitch =>(
    toggleSwitch.addEventListener("change", function() {
    
        // show/hide content
        table = this.closest("table")
        const rows = table.querySelectorAll("tr:not(:first-child)");
        rows.forEach(row => {
            row.style.display = this.checked ? "" : "none";
        });

        fetch(`${this.'endpoint'}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ data: this.checked })
        }).catch(error => console.error("Error sending API request:", error));

        // activate/deactivate function in backend

})));

function updateRPM() {
    fetch('/rpm')
        .then(response => response.json())
        .then(data => document.getElementById('currentRPM').innerText = data.rpm);
}