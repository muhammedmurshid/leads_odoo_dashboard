/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { jsonrpc } from "@web/core/network/rpc_service";
import { rpc } from "@web/core/network/rpc_service";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class CustomDashboard extends Component {

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
        
            jsonrpc('/custom_dashboard/test', {'hello': 'guys'}).then((res)=>{

                console.log(res)
            })
    }



    setStateValues() {

    }
}

CustomDashboard.template = "tijus_odoo_dashboards.dashboard_template";
registry.category("actions").add("custom_dashboard", CustomDashboard);