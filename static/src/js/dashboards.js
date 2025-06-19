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
                const today = new Date();
                const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

                const formatDate = (date) => date.toISOString().split("T")[0];

                this.state = useState({
                    currency: '₹',
                    from_date: formatDate(firstDay),
                    to_date: formatDate(today),
                    
                     dashboardStats: {
                        'sales_today': 0,
                        'sales_this_week': 0,
                        'sales_this_month': 0,
                        'sales_this_quarter': 0,
                        'sales_this_year': 0,
                        'employee_sales_data': [],
                        'product_sales_data': [],
                        'zero_sales_employees':[],
                        'employee_source_data': [],
                        'all_sources':[],
                        'employee_quality_data': [],
                        'lead_quality_keys': [],
                        'lead_quality_labels': [],
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
            fetchDashboardData() {
                // Call the backend with date filters if available
                jsonrpc('/custom_dashboard/get_dashboard_data', {
                    from_date: this.state.from_date,
                    to_date: this.state.to_date
                }).then((res_data) => {
                    this.state.dashboardStats = res_data.dashboardStats;
                });
            }

            filterByDate() {
                // Get date values from input fields
                console.log('hi')
                const fromDateInput = document.getElementById('from_date');
                const toDateInput = document.getElementById('to_date');

                if (fromDateInput && toDateInput) {
                    this.state.from_date = fromDateInput.value;
                    this.state.to_date = toDateInput.value;
                    console.log('hi', this.state.from_date, this.state.to_date)
                    // Fetch dashboard data with filtered dates
                    this.fetchDashboardData();
                }
            }

            // getDomain(api_endpoint, req_domain){
            //     jsonrpc('/custom_dashboard/get_dashboard_data', {'hello': 'guys'}).then((res_data)=>{
            //         this.state.dashboardStats = res_data.dashboardStats
            //     })
            // }

        }

        CustomDashboard.template = "leads_odoo_dashboard.dashboard_template";
        registry.category("actions").add("custom_dashboard", CustomDashboard);