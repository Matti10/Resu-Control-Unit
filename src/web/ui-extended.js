let selectedCircle = null;
const configSetPeriodMs = 3000;
const limiterScaler = 1000;
let colorContainers;
let toggleSwitches;
let pinSelectors;
let debounceTimer;
const debounceTime_ms = 500;
window.config = null;
window.rcuFuncCorrelation = {
    "ShiftLights": {
        "buildFunc": build_shiftLight_table,
        "displayName": "Shift Lights"

    },
    "RPMReader": {
        "buildFunc": build_rpmReader_table,
        "displayName": "RPM Input"

    },
}

window.sampleFunctions = {
    "sample_pattern" : samplePattern,
    "sample_brightness" : sampleBrightness,
    "sample_color" : sampleColor,
}

let configChanged = false;
let funcToRemove = null;


async function getAllConfig() {
    return await getEndpoint("/config/", cacheBust = `?_=${Date.now()}`);
}

async function getEndpoint(post_endpoint, cacheBust = "") {
    try {
        const response = await fetch(`${post_endpoint}${cacheBust}`);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error('Error fetching config:', error);
        return null;
    }
}

function convertpost_endpointToConfigKey(post_endpoint) {
    post_endpoint = post_endpoint.replace("/config", "");
    return post_endpoint.split('/').filter(key => key); // Split the path and filter out empty strings
}

function getLocalConfigFromEndpoint(post_endpoint, config = window.config) {
    const keys = convertpost_endpointToConfigKey(post_endpoint);
    let value = config;

    for (const key of keys) {
        if (value[key] !== undefined) {
            value = value[key];
        } else {
            console.log(`${key} does not exist, likely due to post_endpoint ${post_endpoint} being incorrect`)
            // throw new Error(`${key} does not exist, likely due to post_endpoint ${post_endpoint} being incorrect`)
        }
    }

    return value
}


function setLocalConfigFromEndpoint(post_endpoint, data, config = window.config) {
    const keys = convertpost_endpointToConfigKey(post_endpoint);
    let current = config;
    configChanged = true;

    while (post_endpoint.includes("//")) {
        post_endpoint = post_endpoint.replace("//","/")
    }

    for (let i = 0; i < keys.length; i++) {
        let key = keys[i];

        if (key.includes("[")) {
            key = key.replace("[","").replace("]","")
        }
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

async function setEndpoint(post_endpoint, data, method = "POST") {
    try {
        const response = await fetch(`${post_endpoint}`, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Failed to update ${post_endpoint} with data: ${data} Error: ${response.statusText}`);
        }

        const responseData = await response.text()
        console.log(`Updated ${post_endpoint} with data:`, responseData);

        return responseData;
    } catch (error) {
        console.error(error);
    }
}

function setInnerTextFromEndpoint(element) {
    element.innerText = getLocalEndpoint(element.getAttribute("post_endpoint"))
}

function handle_RCUFunc_configChange(element, data, post_endpoint = null, config = window.config) {
    if (null === post_endpoint) {
        post_endpoint = element.getAttribute("post_endpoint")
    }

    setLocalConfigFromEndpoint(post_endpoint, data)

    const func_table = find_function_table(element)

    if (null !== func_table) {
        setEndpoint(func_table.post_endpoint, config.RCUFuncs[func_table.funcID])
    }
}


function downloadConfig() {
    window.location.href = '/downloadConfig';
}


async function setAllConfig(config = window.config) {
    if (configChanged) {
        configChanged = false;
        const jsonData = JSON.stringify(config);
        //Create a Blob with the JSON data
        const blob = new Blob([jsonData], { type: "application/json" });
        return await uploadConfig(blob);
    }
}


async function uploadLocalConfig(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    return await uploadConfig(file, true)
}

async function uploadConfig(file, alert = false) {
    const fd = new FormData();
    fd.append("file", new File([file], "config.json", { type: "application/json" }));

    return await fetch('/uploadConfig', {
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

function getShiftLightSubKey_fromEndpoint(endpoint) {
    subKey = "Limiter"
    if (!endpoint.includes(subKey)) {
        subKey = "ShiftLights"
    }
    return subKey
}

async function sampleColor(adjustedColor, rcuFuncID = null, endpoint = null) {
    const spoofedColorObj = {
        "id" : selectedCircle.id,
        "color" : adjustedColor
    }
    subkey = getShiftLightSubKey_fromEndpoint(endpoint)
    return await run_method(rcuFuncID, "sample_color", args = [spoofedColorObj, subkey]);
}

async function samplePattern(data, rcuFuncID = null, endpoint = null) {
    const _kwargs = {
        "pattern" : null,
        "period" : null,
        "subKey" : getShiftLightSubKey_fromEndpoint(endpoint) || null // this defaults to "ShiftLights"
    }

    if (endpoint.includes("period")) {
        _kwargs["period"] = data
    } else {
        _kwargs["pattern"] = data

    }

    return await run_method(rcuFuncID, "sample_pattern", kwargs=_kwargs);
}

async function sampleBrightness(newBrightness, rcuFuncID = null, endpoint = null) {
    const _args = [
        newBrightness
    ]
    return await run_method(rcuFuncID, "sample_brightness", args=_args);
}

async function run_sampleFunction(element,data,endpoint=null) {
    const sample_func_id = element.getAttribute("sample_func")
    if (null !== sample_func_id) {
        const rcuFunc_id = find_function_table(element)
        if (null == endpoint) {
            endpoint = element.getAttribute("post_endpoint")
        }
        return await window.sampleFunctions[sample_func_id](data,rcuFunc_id,endpoint)
    }

}

function changeColor(event) {
    // Change the circle's background color
    let newColor = event.target.value;
    selectedCircle.style.backgroundColor = newColor;
    const adjustedColor = applyColorAdjustments(hexToRgb(newColor));
    const func_table = find_function_table(selectedCircle)
    const cirlce_endpoint = selectedCircle.getAttribute("post_endpoint")
    run_sampleFunction(selectedCircle).then(
        () => {
            const post_endpoint = `/RCUFuncs${func_table.post_endpoint}${cirlce_endpoint}/[${selectedCircle.id}]/color`
            handle_RCUFunc_configChange(selectedCircle, adjustedColor, post_endpoint)
        }
    );

}

function addCirle(container, color, id) {
    const circle = document.createElement('div');
    circle.className = 'circle';
    circle.id = `${id}`;
    circle.setAttribute("sample_func", "sample_color")
    circle.setAttribute("post_endpoint", `/ShiftLights/ShiftLights/colors`)
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
        button.setAttribute("post_endpoint", `${container.getAttribute('post_endpoint')}/selected`)
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

    // Remove active class from all buttons
    buttons.forEach(btn => btn.className = "pure-button");

    // Add active class to the clicked button  
    button.className = "pure-button pure-button-active";

    // Send API request with the selected button's ID
    run_sampleFunction(button.parentNode,button.innerText).then(() => {
        handle_RCUFunc_configChange(button, button.innerText);

    });

}



function buildSliderFromEndpoint() {
    const containers = document.getElementsByClassName("slider-container")
    for (const container of containers) {
        const slider = container.getElementsByClassName("sliderBar")[0];
        const inputBox = container.getElementsByClassName("value")[0];
        const post_endpoint = container.getAttribute('post_endpoint');
        const scaler = container.getAttribute('scaler') || 1;
        const value = getLocalConfigFromEndpoint(post_endpoint) * scaler;

        slider.value = value;
        inputBox.value = value;

        // Sync input box with slider
        slider.oninput = function () {
            handleInput(this);
            inputBox.value = this.value;
        };

        // Sync slider with input box (with min/max validation)
        inputBox.oninput = function () {
            if (this.value < slider.min) this.value = slider.min;
            if (this.value > slider.max) this.value = slider.max;
            slider.value = this.value;
            handleInput(this);
        }
    }
}

function handleInput(input) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        const parent = input.parentNode
        const post_endpoint = parent.getAttribute('post_endpoint');
        if (parent.id == "brightNessSlider") {
            setBrightness(post_endpoint, input.value)
        }
        else {
            const scaler = parent.getAttribute('scaler') || 1;
            const scaledData = input.value / scaler
            run_sampleFunction(parent,scaledData,post_endpoint).then(() => {
                handle_RCUFunc_configChange(input,scaledData,post_endpoint);
            });
        }
    }, debounceTime_ms);
}

function buildButtonGroupsFromEndpoint() {
    const buttonGroups = document.getElementsByClassName("pure-button-group")

    for (const buttonGroup of buttonGroups) {
        const buttonInfo = getLocalConfigFromEndpoint(buttonGroup.getAttribute("post_endpoint"))
        populateButtonGroup(buttonGroup, buttonInfo)
    }
}

function buildColorCirclesFromEndpoint() {
    for (const colorContainer of colorContainers) {
        getLocalConfigFromEndpoint(colorContainer.getAttribute("post_endpoint")).forEach(light => {
            addCirle(colorContainer, reverseColorAdjustments(light.color), light.id); //add cirlce making sure to revert color changes made when sending to the server
        });
    }
}

async function setBrightness(element, brightness) {
    const scaled_brightness = brightness / brightnessScaler
    run_sampleFunction(element, scaled_brightness).then(() => { // should really start the color cals and await them and the sample before changing config
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
    
            handle_RCUFunc_configChange(element, brightenedColors,colorContainers[i].getAttribute("post_endpoint"))
        }
    });
}

function unassignFuncsPin(functionName, config = window.config) {
    Object.entries(config.Pins).forEach(([pinNumber, pinData]) => {
        if (pinData["type"] == functionName) {
            pinData["type"] = ""
        }
    });
    configChanged = true;
}

function handlePinSelectionClick(option) {
    const selectedOption = option.options[option.selectedIndex]; // get the data from the selection
    const funcName = option.getAttribute("function-Name")
    option.style.backgroundColor = selectedOption.style.backgroundColor; // update the color of the selector to match
    if (selectedOption.innerText == "Unassigned") {
        unassignFuncsPin(funcName)
    } else {
        setLocalConfigFromEndpoint(selectedOption.post_endpoint, funcName); // the ID to assign the PIN too is stored in function name attr
    }

    // update all pin selectors with the change
    setAllConfig().then(() => {
        getAllConfig().then(config => {
            window.config = config
            buildPinSelectorsFromEndpoint() //rebuilding them all is easy but inefficent #TODO
        });
    });


}


function buildPinSelectorsFromEndpoint(pinConfig = window.config.Pins) {


    pinSelectors.forEach(pinSelector => {
        // Clear existing options (if any)
        pinSelector.innerHTML = '';

        // Create "unassigned" option
        const unassignedOption = document.createElement('option');
        unassignedOption.style.backgroundColor = 'grey';
        unassignedOption.innerText = `Unassigned`;
        unassignedOption.value = ""
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
                option.post_endpoint = `${pinSelector.getAttribute("post_endpoint")}/${pinNumber}/type`

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
    show_loadingScreen()
    build_all()
    populate_RcuFunc_Popup()
});

function rebuild_all(redirect = "") {
    clear_all_dynamic()
    build_all(redirect)
}

function build_all(redirect = "") {
    getAllConfig().then(config => {
        window.config = config
        build_rcuFunction_tables();

        colorContainers = document.querySelectorAll('[class="color-container"]');
        toggleSwitches = document.querySelectorAll('[class="toggleSwitch"]');
        pinSelectors = document.querySelectorAll('.pinSelector-dropdown');
        buildButtonGroupsFromEndpoint();
        buildColorCirclesFromEndpoint();
        buildPinSelectorsFromEndpoint();
        buildSliderFromEndpoint();
        // setInterval(setAllConfig, configSetPeriodMs)
    }).then(() => {
        window.location.hash = redirect
        hide_loadingScreen()
    })
}


function show_loadingScreen() {
    const overlay = document.getElementById("overlay");
    overlay.classList.remove("fade-out");
    // Show overlay
    document.getElementById("overlay").style.display = "flex";
}

function hide_loadingScreen() {
    const overlay = document.getElementById("overlay");
    overlay.classList.add("fade-out");

    setTimeout(() => {
        overlay.style.display = "none";
    }, 500);
}

function updateRPM() {
    fetch('/rpm')
        .then(response => response.json())
        .then(data => document.getElementById('currentRPM').innerText = data.rpm);
}

function find_function_table(element) {
    // Base case: If the element is null or undefined, return null
    if (!element) {
        return null;
    }

    // Check if the current element is a table with the class "function-table"
    if (element.tagName === "TABLE" && element.classList.contains("function-table")) {
        return element;
    }

    // Recurse up to the parent element
    return find_function_table(element.parentElement);
}

function build_function_table(funcID, displayName, container = document.getElementById("mainbody")) {
    displayName = `${displayName} <span style="font-size: 0.8em;display: inline-block; text-align: left;">(${funcID.split("_").at(-1)})</span>`
    const id = `${funcID}-table`
    const table = document.createElement('table');
    table.classList.add("function-table")
    table.id = id;
    table.funcID = funcID
    table.post_endpoint = `/${funcID}`
    table.innerHTML = `
    <tr>
        <td class="table-global-heading" colspan="2">
            <div class="heading-with-tooltip">
                <div>${displayName}</div>
                <div class="tooltip">
                    <img src="/webFiles/close.webp" alt="close" class="close-btn" style="width: 20px; height: 20px;">
                    <span class="tooltiptext">Remove ${displayName} from the RCU</span>
                </div>
            </div>
        </td>
    </tr>`;

    container.appendChild(table);

    // Add click event to close button
    table.querySelector('.close-btn').addEventListener('click', () => {
        funcToRemove = funcID
        openPopup("rmFunc-popup")
    });

    add_sidebar_entry(`${displayName}`, id);

    return table;
}

function add_function_table_row(table, heading, tooltipText, content) {
    const row = document.createElement('tr');
    row.innerHTML = `<th>
                <div class="heading-with-tooltip">
                    ${heading}
                    <div class="tooltip">
                        <img src="/webFiles/info-icon.webp" alt="Info" style="width: 20px; height: 20px;">
                        <span class="tooltiptext">${tooltipText}</span>
                    </div>
                </div>
            </th>
            <td>
                ${content}
            </td>`;
    table.appendChild(row);
}

function add_PinSelection_function_table_row(table, heading, tooltipText, id, allowedClass = "IO") {
    add_function_table_row(
        table,
        heading,
        tooltipText,
        `<select class="pinSelector-dropdown" post_endpoint="/config/Pins" function-name="${id}" allowed-class="${allowedClass}"><!--This is dynamically set by JS --></select>`
    );
}
function add_sidebar_entry(text, href) {
    const sidebar = document.getElementById("func-sidebar");
    const link = document.createElement("li");

    link.className = "pure-menu-item";
    link.href = href;
    link.innerHTML = `<a href="#${href}" class="pure-menu-link">${text}</a>`;
    sidebar.append(link)

}

function clear_all_dynamic() {
    clear_dynamic_content()
    clear_dynamic_sidebar()
};

function clear_dynamic_content() {
    document.getElementById("mainbody").innerHTML = ""

};

function clear_dynamic_sidebar() {
    document.getElementById("func-sidebar").innerHTML = ""
}

function build_shiftLight_table(funcConfig = window.config.RCUFuncs.ShiftLights_0, displayName = "Shift Lights") {

    const funcTable = build_function_table(funcConfig.id, displayName);

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
        `<div class="pure-g"> <div class="pure-u-1-2" post_endpoint="/${shiftLightConfigRoot}/ShiftLights/startRPM" oninput="handleInput(this)">     <label for="name">Start RPM</label>     <input type="text" value=${funcConfig.ShiftLights.startRPM} id="name" name="name" style="width: 60px;"> </div> <div class="pure-u-1-2" post_endpoint="/${shiftLightConfigRoot}/ShiftLights/endRPM" oninput="handleInput(this)">     <label for="name">End RPM</label>     <input type="text" value=${funcConfig.ShiftLights.endRPM} id="name" name="name" style="width: 60px;"> </div> </div>`
    );
    add_function_table_row(
        funcTable,
        `Light Color`,
        `Select the color of each of the 15 shift lights by clicking on the corresponding light below. The color will update once you "click out" of the color picker.`,
        `<div class="color-container" sample_func="sample_color" post_endpoint="${shiftLightConfigRoot}/ShiftLights/colors"> <!--This is dynamically set by JS--></div> <input type="color" id="colorPicker" style="opacity: 0; position: absolute; pointer-events: none;" onchange="changeColor(event)">`
    );
    add_function_table_row(
        funcTable,
        `Rev Pattern`,
        `Select the pattern used through the rev range`,
        `<div id="revPattern-containter" class="pure-button-group" role="group" sample_func="sample_pattern" post_endpoint="${shiftLightConfigRoot}/ShiftLights/pattern" aria-label="..."> </div>`
    );
    add_function_table_row(
        funcTable,
        `Limiter Color`,
        `Select the color the shiftlights change to when the shift point is reached`,
        `<div class="color-container" sample_func="sample_color" post_endpoint="${shiftLightConfigRoot}/Limiter/colors"> <!--This is dynamically set by JS --></div>`
    );
    add_function_table_row(
        funcTable,
        `Limiter Pattern`,
        `Select the pattern used when shift point is reached`,
        `<div id="limiterPattern-containter" class="pure-button-group" role="group" sample_func="sample_pattern" post_endpoint="${shiftLightConfigRoot}/Limiter/pattern" aria-label="..."> </div>`
    );
    add_function_table_row(
        funcTable,
        `Limiter Period (ms)`,
        `This sets speed the limiter plays its pattern (in milliseconds)`,
        `<div class="slider-container" scaler=${limiterScaler} id="limiterPeriodSlider" sample_func="sample_pattern" post_endpoint="${shiftLightConfigRoot}/Limiter/period_s"> <input type="range" class="sliderBar" min="50" max="1000" value="50"> <input type="number" class="value" min="50" max="1000" value="50"> </div>`
    );
    add_function_table_row(
        funcTable,
        `Brightness`,
        `I think you already know what this one does ;). This Controls the Overall Brightness of the shift lights`,
        `<div class="slider-container" scaler=${brightnessScaler} id="brightnessSlider" sample_func="sample_brightness"  post_endpoint="${shiftLightConfigRoot}/brightness"> <input type="range" class="sliderBar" min="0" max="100" value="50"> <input type="number" class="value" min="0" max="100" value="50"> </div>`
    );

}

function build_rpmReader_table(funcConfig, displayName = "RPM Input") {
    const funcTable = build_function_table(funcConfig.id, displayName);
    const rpmReaderConfigRoot = `/RCUFuncs/${funcConfig.id}/${funcConfig.type}` // TODO port this to parent function

    add_function_table_row(
        funcTable,
        `RPM Input Mode`,
        `This tells the RCU where to look for the RPM signal!`,
        `<div id="rpmInput-containter" class="pure-button-group" role="group" post_endpoint="${rpmReaderConfigRoot}/options" aria-label="..."></div>`
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
        `<label for="name"></label><input value="${funcConfig.RPMReader.Tacho.pulsesPerRev || 6}" type="text" id="name" style="width:100%">`
    );
    add_function_table_row(
        funcTable,
        `Current RPM`,
        `The RPM value currently being read by the RCU. If this is wrong try adjusting the input method, or pulses per revolution (tacho mode only)`,
        `<p id="currentRPM">Not Set</p>`
    );
}

function build_rcuFunction_tables(
    config = window.config,
    rcuFuncCorrelation = window.rcuFuncCorrelation
) {
    Object.keys(config.RCUFuncs).forEach(key => {
        rcuConfig = config.RCUFuncs[key]
        rcuFuncCorrelation[rcuConfig.type]["buildFunc"](rcuConfig)
    });

}

function populate_RcuFunc_Popup() {
    const dropdown = document.getElementById('rcuFunc-dropdown');
    Object.keys(rcuFuncCorrelation).forEach(key => {
        const newOption = document.createElement("option")
        newOption.value = key
        newOption.innerHTML = rcuFuncCorrelation[key]["displayName"]
        dropdown.append(newOption)
    });
}

function openPopup(popoupID) {
    document.getElementById(popoupID).style.display = 'block';
    document.getElementById('popup-overlay').style.display = 'block';
}

function closePopup(popoupID) {
    document.getElementById(popoupID).style.display = 'none';
    document.getElementById('popup-overlay').style.display = 'none';
}

function confirmFuncSelection(button) {
    button.disabled = true
    show_loadingScreen()
    const selected = document.getElementById('rcuFunc-dropdown').value;
    console.log('Selected:', selected);
    // Pass the selected value to your function
    add_rcuFunction(selected).then(response => {
        console.log(response)
        rebuild_all(`${response}-table`);
        closePopup("addFunc-popup");
        button.disabled = false

    });


}

function confirmFuncRemove(button) {
    button.disabled = true
    show_loadingScreen()
    rm_rcuFunction(funcToRemove).then(() => {
        rebuild_all();
        closePopup("rmFunc-popup");
        button.disabled = false
    })
    funcToRemove = null;
}


async function run_method(post_endpoint, method, args = [], kwargs = {}) {
    if (!Array.isArray(args)) {
        args = [args]
    }
    if (typeof kwargs !== "object") {
        throw "Kwargs must be an object of key value pairs"
    }
    const data = {
        "func": method,
        "kwargs": kwargs,
        "args": args
    }
    return await setEndpoint(post_endpoint, data, method = "PUT")
}

async function add_rcuFunction(funcType, post_endpoint = "/RCU") {
    await run_method(post_endpoint, "add_RCUFunc", args = funcType)
    return await run_method(post_endpoint, "export_config")
}

async function rm_rcuFunction(id, post_endpoint = "/rmFunc") {
    return await setEndpoint(post_endpoint, id)
}