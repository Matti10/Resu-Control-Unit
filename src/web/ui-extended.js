let selectedCircle = null;
const configSetPeriodMs = 3000;
const limiterScaler = 1000;
let colorContainers;
let toggleSwitches;
let pinSelectors;
window.config = null;
let configChanged = false;


async function getAllConfig() {
    return await getEndpoint("/config/");
}

async function getEndpoint(endpoint) {
    try {
        const response = await fetch(endpoint);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error('Error fetching config:', error);
        return null;
    }
}

function convertEndpointToConfigKey(endpoint) {
    endpoint = endpoint.replace("/config", "");
    return endpoint.split('/').filter(key => key); // Split the path and filter out empty strings
}

function getLocalConfigFromEndpoint(endpoint, config = window.config) {
    const keys = convertEndpointToConfigKey(endpoint);
    let value = config;

    for (const key of keys) {
        if (value[key] !== undefined) {
            value = value[key];
        } else {
            console.log(`${key} does not exist, likely due to endpoint ${endpoint} being incorrect`)
            // throw new Error(`${key} does not exist, likely due to endpoint ${endpoint} being incorrect`)
        }
    }

    return value
}


function setLocalConfigFromEndpoint(endpoint, data, config = window.config) {
    const keys = convertEndpointToConfigKey(endpoint);
    let current = config;
    configChanged = true;

    for (let i = 0; i < keys.length; i++) {
        const key = keys[i];

        // If it's the last key, set the value
        if (i === keys.length - 1) {
            current[key] = data;
        } else {
            // If the key doesn't exist or isn't an object, create an empty object
            if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
                current[key] = {};
            }
            current = current[key];
        }
    }
}

async function setEndpoint(endpoint, data) {

    await fetch(`${endpoint}`, {
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
    element.innerText = getLocalEndpoint(element.getAttribute("endpoint"))
}



function downloadConfig() {
    window.location.href = '/downloadConfig';
}


function setAllConfig(config = window.config) {
    if (configChanged) {
        configChanged = false;
        const jsonData = JSON.stringify(config);
        //Create a Blob with the JSON data
        const blob = new Blob([jsonData], { type: "application/json" });
        uploadConfig(blob);
    }
}


function uploadLocalConfig(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    uploadConfig(file,true)
}

function uploadConfig(file,alert=false) {
    const fd = new FormData();
    fd.append("file", new File([file], "config.json", { type: "application/json" }));
    
    fetch('/uploadConfig', {
        method: 'POST',
        body: fd
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (alert) {
                alert('File uploaded successfully');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (alert) {
                alert('File upload failed');
            }
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

    setLocalConfigFromEndpoint(`${endpoint}/[${id}]/color`, requestBody)
}

function changeColor(event) {
    // Change the circle's background color
    let newColor = event.target.value;
    selectedCircle.style.backgroundColor = newColor;

    postColorChange(selectedCircle.getAttribute("endpoint"), selectedCircle.id, newColor)
}

function addCirle(container, color, id) {
    const circle = document.createElement('div');
    circle.className = 'circle';
    circle.id = `${id}`;
    circle.setAttribute("endpoint", `/ShiftLights/ShiftLights/colors`)
    circle.onclick = function () { pickColor(this); };

    // Convert color values to CSS format
    circle.style.backgroundColor = `rgb(${color.r}, ${color.g}, ${color.b})`;

    container.appendChild(circle);  // Append to shiftColor-container
}

function populateButtonGroup(container, buttonData) {
    let selected = buttonData.selected
    buttonData.options.forEach(pattern => {
        const button = document.createElement('button');
        button.id = `${pattern}-${container.id}`;
        button.innerText = pattern;
        button.setAttribute("endpoint", `${container.getAttribute('endpoint')}/selected`)
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
    let endpoint = button.getAttribute('endpoint')

    // Remove active class from all buttons
    buttons.forEach(btn => btn.className = "pure-button");

    // Add active class to the clicked button  
    button.className = "pure-button pure-button-active";

    // Send API request with the selected button's ID
    setLocalConfigFromEndpoint(endpoint, button.innerText);

}



function buildSliderFromEndpoint() {
    const containers = document.getElementsByClassName("slider-container")
    for (const container of containers) {
        const slider = container.getElementsByClassName("sliderBar")[0];
        const inputBox = container.getElementsByClassName("value")[0];
        const endpoint = container.getAttribute('endpoint');
        const scaler = container.getAttribute('scaler') || 1;
        const value = getLocalConfigFromEndpoint(endpoint) * scaler;

        slider.value = value;
        inputBox.value = value;

        // Sync input box with slider
        slider.oninput = function () {
            handleSliderInput(this);
            inputBox.value = this.value;
        };

        // Sync slider with input box (with min/max validation)
        inputBox.oninput = function () {
            if (this.value < slider.min) this.value = slider.min;
            if (this.value > slider.max) this.value = slider.max;
            slider.value = this.value;
            handleSliderInput(this);
        }
    }
}

function handleSliderInput(slider) {
    let parent = slider.parentNode
    let endpoint = parent.getAttribute('endpoint');
    if (parent.id == "brightNessSlider") {
        setBrightness(endpoint, slider.value)
    }
    else {
        let scaler = parent.getAttribute('scaler') || 1;
        setLocalConfigFromEndpoint(endpoint, slider.value / scaler);
    }

}

function buildButtonGroupsFromEndpoint() {
    const buttonGroups = document.getElementsByClassName("pure-button-group")

    for (const buttonGroup of buttonGroups) {
        const buttonInfo = getLocalConfigFromEndpoint(buttonGroup.getAttribute("endpoint"))
        populateButtonGroup(buttonGroup, buttonInfo)
    }
}

function buildColorCirclesFromEndpoint() {
    for (const colorContainer of colorContainers) {
        getLocalConfigFromEndpoint(colorContainer.getAttribute("endpoint")).forEach(light => {
            addCirle(colorContainer, reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
        });
    }
}


function toggleTableRows(element, post = true) {
    // show/hide content
    table = element.closest("table")
    const rows = table.querySelectorAll("tr:not(:first-child)");
    rows.forEach(row => {
        row.style.display = element.checked ? "" : "none";
    });
    if (post) {
        setLocalConfigFromEndpoint(element.getAttribute("endpoint"), element.checked);
    }
}

function buildToggleSwitchesFromEndpoint() {
    for (const toggleSwitch of toggleSwitches) {
        toggleSwitch.checked = getLocalConfigFromEndpoint(toggleSwitch.getAttribute("endpoint"));
        toggleSwitch.addEventListener("change", function () {
            toggleTableRows(this); // `this` refers to `toggleSwitch`
        });
        toggleTableRows(toggleSwitch, post = false)
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
                color: applyColorAdjustments(rgbStringToObject(color), brightness / brightnessScaler) // divide by brightnessScaler as brightness is stor as a float between 0 and 1 on server
            };
        });

        // Store the fetch promise
        await setLocalConfigFromEndpoint(colorContainers[i].getAttribute("endpoint"), brightenedColors)
        if (i < 1) {
            setLocalConfigFromEndpoint(endpoint, brightness / brightnessScaler) // divide by brightnessScaler as brightness is stor as a float between 0 and 1 on server
        }
    }
}


function handlePinSelectionClick(option) {
    const selectedOption = option.options[option.selectedIndex]; // get the data from the selection
    option.style.backgroundColor = selectedOption.style.backgroundColor; // update the color of the selector to match
    setLocalConfigFromEndpoint(selectedOption.endpoint, option.getAttribute("function-Name")); // the ID to assign the PIN too is stored in function name attr

    // update all pin selectors with the change
    buildPinSelectorsFromEndpoint() //rebuilding them all is easy but inefficent #TODO
}


function buildPinSelectorsFromEndpoint(pinConfig = window.config.Pins) {

    // Create "unassigned" option
    const unassignedOption = document.createElement('option');
    unassignedOption.style.backgroundColor = 'grey';
    unassignedOption.innerText = `Unassigned`;

    pinSelectors.forEach(pinSelector => {
        // Clear existing options (if any)
        pinSelector.innerHTML = '';

        //add unassigned option
        pinSelector.appendChild(unassignedOption);


        // default selection to  
        unassignedOption.selected = true;

        const allowedClass = pinSelector.getAttribute('allowed-class');

        Object.entries(pinConfig).forEach(([pinNumber, pinData]) => {
            // Only add options that are "allowed"
            if (pinData.class.includes(allowedClass)) {
                const option = document.createElement('option');
                option.value = pinNumber;  // Use pinNumber as the value
                option.endpoint = `${pinSelector.getAttribute("endpoint")}/${pinNumber}/type`

                // get assignment data. This is called in a loop during build so not very efficent... Code is tidier though?
                const pinFunction = pinSelector.getAttribute('function-Name');

                if (pinData.type !== "" && pinData.type !== pinFunction) { //if the pin is assigned to another function
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
                if (pinFunction === pinData.type) {
                    option.selected = true;
                    pinSelector.style.backgroundColor = option.style.backgroundColor;
                }

                pinSelector.appendChild(option);
            }
        });

        // Add event listener to change the background color of the selection box and make API call
        pinSelector.addEventListener('change', function () {
            handlePinSelectionClick(this)
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    getAllConfig().then(config => {
        window.config = config

        // build_shiftLight_table()
        build_rpmReader_table(window.config.RCUFuncs.RPMReader_3)

        colorContainers = document.querySelectorAll('[class="color-container"]');
        toggleSwitches = document.querySelectorAll('[class="toggleSwitch"]');
        pinSelectors = document.querySelectorAll('.pinSelector-dropdown');
        buildButtonGroupsFromEndpoint();
        buildColorCirclesFromEndpoint();
        buildPinSelectorsFromEndpoint();
        buildSliderFromEndpoint();
        buildToggleSwitchesFromEndpoint();

        setInterval(setAllConfig,configSetPeriodMs)
    });
});


function updateRPM() {
    fetch('/rpm')
        .then(response => response.json())
        .then(data => document.getElementById('currentRPM').innerText = data.rpm);
}

function build_function_table(funcID, displayName, container = document.getElementById("mainbody")) {
    const table = document.createElement('table');
    table.id = `${funcID}-table`;
    table.innerHTML = `<tr>
        <td class="table-global-heading" colspan="2">
            <div class="heading-with-tooltip">
                ${displayName}
            </div>
        </td>
    </tr>`;

    container.appendChild(table);

    return table;
}

function add_function_table_row(table, heading, tooltipText, content) {
    const row = document.createElement('tr');
    row.innerHTML = `<th>
                <div class="heading-with-tooltip">
                    ${heading}
                    <div class="tooltip">
                        <img src="/webFiles/info-icon.png" alt="Info" style="width: 20px; height: 20px;">
                        <span class="tooltiptext">${tooltipText}</span>
                    </div>
                </div>
            </th>
            <td>
                ${content}
            </td>`;
    table.appendChild(row);
}

function add_PinSelection_function_table_row(table,heading,tooltipText, id, allowedClass = "IO") {
    add_function_table_row(
        table,
        heading,
        tooltipText,
        `<select class="pinSelector-dropdown" endpoint="/config/Pins" function-name="${id}" allowed-class="${allowedClass}"><!--This is dynamically set by JS --></select>`
    );
}
function add_sidebar_entry(text, href) {
    const sidebar = document.getElementById("sidebar");
    const link = document.createElement("li");

    link.className = "pure-menu-link";
    link.href = href;
    link.innerHTML = `<a href="${href}" class="pure-menu-link">${text}</a>`;


}

function build_shiftLight_table(funcConfig = window.config.RCUFuncs.ShiftLights_0, displayName = "Shift Lights") {
    const funcTable = build_function_table(funcConfig.id, displayName);
    add_sidebar_entry(displayName, `#${funcTable.id}`);

    const shiftLightConfigRoot = `/RCUFuncs/${funcConfig.id}/${funcConfig.type}`; // TODO port this to parent function
    add_PinSelection_function_table_row(
        funcTable,
        `Shift Light Output Pin`,
        `Select the pin you've connected the shift light signal wire too`,
        funcConfig.id,
        "O"
    );
    add_function_table_row(
        funcTable,
        `RPM Range Selection`,
        `Select the rpm range you want the lights to display. Any rpm over the Max RPM value will trigger the limiter pattern/colors`,
        `<div class="pure-g"> <div class="pure-u-1-2">     <label for="name">Start RPM</label>     <input type="text" value=${funcConfig.ShiftLights.startRPM} id="name" name="name" style="width: 60px;"> </div> <div class="pure-u-1-2">     <label for="name">End RPM</label>     <input type="text" value=${funcConfig.ShiftLights.endRPM} id="name" name="name" style="width: 60px;"> </div> </div>`
    );
    add_function_table_row(
        funcTable,
        `Light Color`,
        `Select the color of each of the 15 shift lights by clicking on the corresponding light below. The color will update once you "click out" of the color picker.`,
        `<div class="color-container"  endpoint="${shiftLightConfigRoot}/ShiftLights/colors"> <!--This is dynamically set by JS--></div> <input type="color" id="colorPicker" style="opacity: 0; position: absolute; pointer-events: none;" onchange="changeColor(event)">`
    );
    add_function_table_row(
        funcTable,
        `Rev Pattern`,
        `Select the pattern used through the rev range`,
        `<div id="revPattern-containter" class="pure-button-group" role="group"  endpoint="${shiftLightConfigRoot}/ShiftLights/pattern" aria-label="..."> </div>`
    );
    add_function_table_row(
        funcTable,
        `Limiter Color`,
        `Select the color the shiftlights change to when the shift point is reached`,
        `<div class="color-container"  endpoint="${shiftLightConfigRoot}/Limiter/colors"> <!--This is dynamically set by JS --></div>`
    );
    add_function_table_row(
        funcTable,
        `Limiter Pattern`,
        `Select the pattern used when shift point is reached`,
        `<div id="limiterPattern-containter" class="pure-button-group" role="group"  endpoint="${shiftLightConfigRoot}/Limiter/pattern" aria-label="..."> </div>`
    );
    add_function_table_row(
        funcTable,
        `Limiter Period (ms)`,
        `This sets the rate that limiter pattern increments!`,
        `<div class="slider-container" scaler=${limiterScaler} id="limiterPeriodSlider" endpoint="${shiftLightConfigRoot}/Limiter/period_s"> <input type="range" class="sliderBar" min="50" max="1000" value="50"> <input type="number" class="value" min="50" max="1000" value="50"> </div>`
    );
    add_function_table_row(
        funcTable,
        `Brightness`,
        `Controls the Overall Brightness of the shift lights`,
        `<div class="slider-container" scaler=${brightnessScaler} id="brightnessSlider" endpoint="${shiftLightConfigRoot}/brightness"> <input type="range" class="sliderBar" min="0" max="100" value="50"> <input type="number" class="value" min="0" max="100" value="50"> </div>`
    );

}

function build_rpmReader_table(funcConfig, displayName = "RPM Input") {
    const funcTable = build_function_table(funcConfig.id, displayName);
    add_sidebar_entry(displayName, `#${funcTable.id}`);
    const rpmReaderConfigRoot = `/RCUFuncs/${funcConfig.id}/${funcConfig.type}` // TODO port this to parent function

    add_function_table_row(
        funcTable,
        `RPM Input Mode`,
        `This tells the RCU where to look for the RPM signal!`,
        `<div id="rpmInput-containter" class="pure-button-group" role="group" endpoint="${rpmReaderConfigRoot}/options" aria-label="..."></div>`
    );
    add_PinSelection_function_table_row(
        funcTable,
        `RPM Input Selection`,
        `Select the pin you've connected the Tacho input too.This can be left unassigned if using the shiftlights in CAN mode`,
        funcConfig.id,
        "I"
    );
    add_function_table_row(
        funcTable,
        `Pulses Per Revolution`,
        `Please enter the number of pulses your RPM sensor sends per engine revolution. This number is typically 6 or 8 and acts as a scaler for the RPM value. If you're unsure, adjust the number below until the current RPM value matches your tacho`,
        `<label for="name"></label><input value="${funcConfig.RPMReader.Tacho.pulsesPerRev || 6}" type="text" id="name" name="name">`
    );
    add_function_table_row(
        funcTable,
        `Current RPM`,
        `The RPM value currently being read by the RCU. If this is wrong try adjusting the input method, or pulses per revolution (tacho mode only)`,
        `<p id="currentRPM">Not Set</p>`
    );
}