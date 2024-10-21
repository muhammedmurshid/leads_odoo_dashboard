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
        this.user_id = false

        this.initializeStateValues();

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        onWillStart(async () => {
            jsonrpc('/custom_dashboard/get_dashboard_data', {'hello': 'guys'}).then((res_data)=>{
                this.state.dashboardStats = res_data.dashboardStats
            })
          });
        
    }


    initializeStateValues() {
        this.state = useState({
            currency: '₹',
            dashboardStats: {
                'sales_today': 0,
                'sales_this_week':0,
                'sales_this_month':0,
                'sales_this_quarter':0,
                'sales_this_year':0,
            }
        })
    }

    callWindowAction(action_model, period){
        var self = this;
        let action = {}
        if(action_model=='sale.order'){

            action = {
                type: 'ir.actions.act_window',
                name: name,
                res_model: model,
                view_mode: 'kanban',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
                context: { 'create': false },
                domain: domain,
            }
        }
        console.log(this)
        // this.action.doAction(action_data)
    }

    // getDomain(api_endpoint, req_domain){
    //     jsonrpc('/custom_dashboard/get_dashboard_data', {'hello': 'guys'}).then((res_data)=>{
    //         this.state.dashboardStats = res_data.dashboardStats
    //     })
    // }

}

CustomDashboard.template = "tijus_odoo_dashboards.dashboard_template";
registry.category("actions").add("custom_dashboard", CustomDashboard);