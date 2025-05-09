/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { BomOverviewComponent } from "@mrp/components/bom_overview/mrp_bom_overview";
import { useService } from "@web/core/utils/hooks";
import { download } from "@web/core/network/download";
//import session from "web.session";
//import { unblockUI } from "web.framework";


patch(BomOverviewComponent.prototype, {
    setup() {
        super.setup();
        this.exportService = useService("action");
    },
    onExportXLSX() {
        debugger;
        download({
            data: {
                data: 1,
                unfolded: true
            },
            url: "/fal_bom_xls_report/download",
        });
    }
});