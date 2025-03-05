let selectedCircle = null;

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

function pickLimiterPattern(buttonId) {
    const buttons = document.querySelectorAll(".limiterPattern-containter button");

    // Remove active class from all buttons
    buttons.forEach(btn => btn.className = "pure-button");

    // Add active class to the clicked button
    document.getElementById(buttonId).className = "pure-button pure-button-active";

    // Send API request with the selected button's ID
    fetch("/ShiftLights/Limiter/pattern", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ pattern: buttonId })
    }).catch(error => console.error("Error sending API request:", error));
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

function changeColor(event) {
    // Change the circle's background color
    let newColor = event.target.value;
    selectedCircle.style.backgroundColor = newColor;
    let endpoint = selectedCircle.parentNode.getAttribute('data-endpoint')

    // Prepare the request payload
    const requestBody = {
        color:  applyColorAdjustments(hexToRgb(newColor)) //apply color adjustments before sending to the server
    };

    // Send a POST request to your API
    fetch(`${endpoint}/${selectedCircle.id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to update color: ${response.statusText}`);
            }
            return response;
        })
        .then(data => console.log("Color update successful:", data))
        .catch(error => console.error("Error updating color:", error));
}

function addCirle(container, color, id) {
    const circle = document.createElement('div');
    circle.className = 'circle';
    circle.id = `${id}`;
    circle.onclick = function () { pickColor(this); };

    // Convert color values to CSS format
    circle.style.backgroundColor = `rgb(${color.red}, ${color.green}, ${color.blue})`;

    container.appendChild(circle);  // Append to shiftLight-container
}

function populateButtonGroup(container,buttonData) {
    let selected = buttonData.selected
    buttonData.patterns.forEach(pattern => {
        const button = document.createElement('button');
        button.id = pattern;
        button.innerText = pattern;
        button.onclick = function () { pickLimiterPattern(pattern); };
    
        if (pattern === selected) {
            button.className = "pure-button pure-button-active";
        } else {
            button.className = "pure-button";
        }
        container.appendChild(button);
    });
}

function buildBrightnessSlider(data) {
    const brightnessSlider = document.getElementById("brightnessSlider");
    const brightnessInputBox = document.getElementById("brightnessValue");
    
    brightnessSlider.value = data.brightness * 100 //times 100 as value is stored as float between 1 and 0 but displayed as int between 0 and 100
    brightnessInputBox.value = data.brightness * 100 

    // Sync input box with brightnessSlider
    brightnessSlider.oninput = function() {
        brightnessInputBox.value = this.value;
        setBrightness(this.value)
    };

    // Sync brightnessSlider with input box (with min/max validation)
    brightnessInputBox.oninput = function() {
        if (this.value < brightnessSlider.min) this.value = brightnessSlider.min;
        if (this.value > brightnessSlider.max) this.value = brightnessSlider.max;
        brightnessSlider.value = this.value;
        setBrightness(this.value)
    };
}

function setBrightness(brightness) {
    // Send API request with the selected button's ID
    fetch("config/ShiftLights/brightness", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ brightness: brightness/100 }) // divide by 100 as brightness is stored as a float between 0 and 1 on server
    }).catch(error => console.error("Error sending API request:", error));
}

function buildWhiteBalanceInputs()

document.addEventListener("DOMContentLoaded", () => {
    fetch('/config/ShiftLights')
        .then(response => response.json())
        .then(data => {
            setColorGlobals(data); // set color modification parameters

            // shift light circles
            data.ShiftLights.forEach(light => {
                addCirle(document.querySelector('.shiftLight-container'), reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
            });

            // limiter circles
            data.LimiterColor.forEach(light => {
                addCirle(document.querySelector('.limiterColor-container'), reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
            });

            // button groups
            populateButtonGroup( document.querySelector('.limiterPattern-containter'),data.Limiter.pattern);// limiter pattern buttons
            populateButtonGroup( document.querySelector('.revPattern-containter'),data.ShiftLights.pattern);// rev pattern buttons
            
            // brightness slider
            buildBrightnessSlider(data);

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
                    const endpoint = pinSelector.getAttribute('data-endpoint');
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
});
