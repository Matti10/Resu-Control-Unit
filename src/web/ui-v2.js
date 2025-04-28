class tableRow {
    constructor (
        id,
        name,
        table,
        hint,
        dataAttr,
        getsetEnpoint,
        sampleKwargs = {},
        sampleArgs = [],
        sampleMethod = null,
        sampleEndpoint = null

    ) {
        this.id = id
        this.name = name
        this.table = table
        this.hint = hint
        this.getsetEnpoint = getsetEnpoint
        this.sampleKwargs = sampleKwargs
        this.sampleMethod = sampleMethod
        this.sampleEndpoint = sampleEndpoint
        this.sampleArgs = sampleArgs


        this.row = document.createElement('tr');
        this.content = ""
    }

    async sampleData() {
        if (null != this.sampleMethod) {
            run_method(this.sampleEndpoint, this.sampleMethod,this.sampleArgs,this.sampleKwargs)
        }
    }

    getData() {

    }

    setData() {
        this.row.innerHTML = this.toHTML()
        this.table.appendChild()
    }

    toHTML() {
        return `<th>
                <div class="heading-with-tooltip">
                    ${this.name}
                    <div class="tooltip">
                        <img src="/webFiles/info-icon.webp" alt="Info" style="width: 20px; height: 20px;">
                        <span class="tooltiptext">${this.hint}</span>
                    </div>
                </div>
            </th>
            <td>
                ${this.content}
            </td>`;
    }
}

class pinSelector extends tableRow {
    
}

class sampeFunctionData {

}