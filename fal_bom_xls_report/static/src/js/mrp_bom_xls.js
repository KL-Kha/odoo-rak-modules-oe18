/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { BomOverviewComponent } from "@mrp/components/bom_overview/mrp_bom_overview";
import { BomOverviewControlPanel } from "@mrp/components/bom_overview_control_panel/mrp_bom_overview_control_panel";
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
        const active_id = this.props.action.context.active_id;
        download({
            data: {
                data: active_id,
                unfolded: true
            },
            url: "/fal_bom_xls_report/download",
        });
    },

    get controlPanelProps() {
        return {
            ...super.controlPanelProps,
            exportXLSX: this.exportXLSX,
        };
    },
});

patch(BomOverviewControlPanel, {
    props: {
        ...BomOverviewControlPanel.props,
        exportXLSX: Function,
    },
});