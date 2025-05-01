class tableRow {
    constructor (
        id,
        name,
        table,
        hint,
        data
    ) {
        this.id = id
        this.name = name
        this.element = table
        this.hint = hint
        this.row = document.createElement('tr');
        this.data = data
    }

    build() {
        this.row.innerHTML = `<th>
            <div class="heading-with-tooltip">
                ${this.name}
                <div class="tooltip">
                    <img src="/webFiles/info-icon.webp" alt="Info" style="width: 20px; height: 20px;">
                    <span class="tooltiptext">${this.hint}</span>
                </div>
            </div>
        </th>`;

        this.row.appendChild(this.data.build())
        return this.row
    }
}

class table {
    constructor (
        funcID,
        displayName,
        rows,
        container = document.getElementById("mainbody"),
    ) {
        this.funcID = funcID
        this.displayName = displayName
        this.container = container
        this.rows = rows
    }

    build() {
        const displayName = `${this.displayName} <span style="font-size: 0.8em;display: inline-block; text-align: left;">(${this.funcID.split("_").at(-1)})</span>`
        const id = `${this.funcID}-table`
        this.element = document.createElement('table');
        this.element.classList.add("function-table")
        this.element.id = id;
        this.element.funcID = this.funcID
        this.element.post_endpoint = `/${this.funcID}`
        this.element.innerHTML = `
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
    
        this.container.appendChild(this.element);
        
        // Add click event to close button
        this.element.querySelector('.close-btn').addEventListener('click', () => {
            funcToRemove = funcID
            openPopup("rmFunc-popup")
        });
    
        // add_sidebar_entry(`${displayName}`, id);
    
        this.rows.forEach(row => {
            this.add_row(row)
        });
    }

    add_row(tableRow) {
        this.element.appendChild(tableRow.build())
    }
}


class tableRowData {
    constructor (
        dataGetter,
        dataSetter,
        writePath,
        sample_func = null,
        builder,
        write_handler
    ) {
        this.dataGetter = dataGetter
        this.dataSetter = dataSetter
        this.sample_func = sample_func
        this.writePath = writePath
        this.write_handler = write_handler
        this.builder = builder
    }

    async changeHandler () {
        this.sample().then(

        )
    }

    async write() {
        this.write_handler(this.dataGetter(),this.writePath)
    }

    
    async sample() {
        if (null != this.sample_func) {
            await this.sample_func(this.dataGetter(),this.sampleEndpoint)
        } else {
            await Promise.resolve()
        }
    }

    build() {
        this.builder()
    }
}

class slider extends tableRowData {
    constructor (
        max,
        min,
        value,
        scaler = 1,
        sample_func = Promise.resolve,
        writePath,
    ) {
        super(
            null, // Placeholder for dataGetter
            null, // Placeholder for dataSetter
            writePath,
            sample_func,
            sample_func
        );
        this.max = max;
        this.min = min;
        this.value = value;
        this.scaler = scaler;
        this.element = document.createElement("td");
        this.debounceTimer = null;
        this.debounceTime_ms = 500;

        // Assign methods after super call
        this.dataGetter = this.getData.bind(this);
        this.dataSetter = this.setData.bind(this);

    }

    changeHandler() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            const scaler = parent.getAttribute('scaler') || 1;
            const scaledData = input.value / scaler

            // # run sample
            run_sampleFunction(parent,this.getData(),post_endpoint).then(() => {
                handle_RCUFunc_configChange(input,scaledData,post_endpoint);
            });
        }, this.debounceTime_ms);
    }
    
    setData (data) {
        this.value = data * this.scaler
        this.element.querySelectorAll('input').forEach(input => {
            input.value = this.value;
        });
    }

    getData () {
        return this.value/this.scaler;
    }

    build () {
        this.div = document.createElement("div")
        this.div.classList.add("slider-container")

        this.slider = this.createSliderBar()
        this.div.appendChild(this.slider)
        this.textInput = this.createSliderTextInput() 
        this.div.appendChild(this.textInput)
        return this.div
    }
    
    createSliderTextInput() {
        const input = document.createElement('input');
        input.type = 'range';
        input.className = 'sliderBar';
        input.min = this.min;
        input.max = this.max;
        input.value = this.max;
        
        return input
    }

    createSliderBar() {
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'value';
        input.min = this.min;
        input.max = this.max;
        input.value = this.value;

        return input
    }
} 

document.addEventListener("DOMContentLoaded", () => {
    window.rowData = new slider(100,1,50,3)
    window.rowData2 = new slider(100,90,90,1)
    window.testRow = new tableRow("any","any",window.funcTable,"sugma",window.rowData)
    window.testRow2 = new tableRow("any2","any2",window.funcTable,"sugma2",window.rowData2)
    window.funcTable = new table("Test","test",[rowData,rowData2],document.getElementById("mainbody"))
    window.funcTable.build()
    window.funcTable.add_row(window.testRow)
});