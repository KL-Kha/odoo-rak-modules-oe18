/** @odoo-module **/

import { registry } from "@web/core/registry";
import { many2OneField } from "@web/views/fields/many2one/many2one_field";
import { browser } from "@web/core/browser/browser";

let hasPermission = false;

// Check permission using XMLHttpRequest
const xhr = browser.XMLHttpRequest ? new browser.XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
xhr.open("POST", "/web/mjb_create_and_edit_many2one/check_permission", false);  // false makes it synchronous
xhr.setRequestHeader("Content-Type", "application/json");
try {
    xhr.send(JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {},
    }));
    if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        hasPermission = response.result;
    }
    else {
        console.log("[mjb_create_and_edit_many2one] Failed to check permission:", xhr.status);
        hasPermission = false;
    }
} catch (error) {
    console.log("[mjb_create_and_edit_many2one] Failed to check permission:", error);
    hasPermission = false;
}

// Create a new field definition that extends the original
registry.category("fields").add("many2one", {
    ...many2OneField,
    component: many2OneField.component,
    extractProps({ attrs, context, decorations, options, string }, dynamicInfo) {
        const props = many2OneField.extractProps(...arguments);
        
        // Set permissions based on check result
        props.canCreate = hasPermission;
        props.canWrite = hasPermission;
        props.canQuickCreate = hasPermission;
        props.canCreateEdit = hasPermission;

        console.log("Many2One field props with permissions:", props);
        return props;
    },
}, { force: true });