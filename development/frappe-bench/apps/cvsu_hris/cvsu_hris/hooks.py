app_name = "cvsu_hris"
app_title = "CvSU HRIS"
app_publisher = "CvSU"
app_description = "CvSU HRIS"
app_email = "mis@cvsu.edu.ph"
app_license = "mit"
fixtures = ['Letter Head', 'Client Script','Gender','Category','Branch','Office',
            'Unit','Employment Status','HR Settings', 'Position','Salutation','Schedule Label',
            {
                "doctype": "Module Profile",
                "filters": [
                    ["name", "in", ["CvSU Employee Module Profile", "CvSU Stock and Asset Module Profile", "CvSU Accounting Module Profile"]]
                ]
            },
            {
                "doctype": "Role Profile",
                "filters": [
                    ["name", "in", ["CvSU Employee Role Profile", "CvSU WFH Employee Role Profile", "CvSU Stock and Asset Role Profile", "CvSU Accounting Role Profile"]]
                ]
            },
            {"doctype": "Role"},
            {"doctype": "Designation", "filters":[ ["custom_office", "not in", ("")] ]}
            ]
required_apps = ["frappe/hrms", "frappe/payments"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cvsu_hris/css/cvsu_hris.css"
app_include_css = "/assets/cvsu_hris/css/custom_styles.css"
# app_include_js = "/assets/cvsu_hris/js/cvsu_hris.js"


# include js, css files in header of web template
# web_include_css = "/assets/cvsu_hris/css/cvsu_hris.css"
# web_include_js = "/assets/cvsu_hris/js/cvsu_hris.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cvsu_hris/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "cvsu_hris/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"
website_context = {
    "favicon": "/assets/cvsu_hris/images/favicon.ico"
}
# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "cvsu_hris.utils.jinja_methods",
#	"filters": "cvsu_hris.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cvsu_hris.install.before_install"
# after_install = "cvsu_hris.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cvsu_hris.uninstall.before_uninstall"
# after_uninstall = "cvsu_hris.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "cvsu_hris.utils.before_app_install"
# after_app_install = "cvsu_hris.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "cvsu_hris.utils.before_app_uninstall"
# after_app_uninstall = "cvsu_hris.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cvsu_hris.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

doc_events = {
    "Employee": {
        # "before_insert": "cvsu_hris.cvsu_hris.overrides.events.Employee.before_insert",
        "before_validate": "cvsu_hris.cvsu_hris.overrides.events.Employee.before_validate",
        "before_save": "cvsu_hris.cvsu_hris.overrides.events.Employee.before_save",
        "after_insert": "cvsu_hris.cvsu_hris.overrides.events.Employee.after_insert"
    },
    "User": {
        "before_save": "cvsu_hris.cvsu_hris.overrides.events.User.before_save"
    },
    "Daily Time Record": {
        "before_validate": "cvsu_hris.cvsu_hris.overrides.events.daily_time_record.before_validate",
        "before_save": "cvsu_hris.cvsu_hris.overrides.events.daily_time_record.before_save"
    },
    "Service Record": {
        "before_validate": "cvsu_hris.cvsu_hris.overrides.events.service_record.before_validate",
    }    
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"cvsu_hris.tasks.all"
#	],
#	"daily": [
#		"cvsu_hris.tasks.daily"
#	],
#	"hourly": [
#		"cvsu_hris.tasks.hourly"
#	],
#	"weekly": [
#		"cvsu_hris.tasks.weekly"
#	],
#	"monthly": [
#		"cvsu_hris.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "cvsu_hris.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.doctype.event.event.get_events": "cvsu_hris.event.get_events"
    "hrms.hr.doctype.employee_checkin.employee_checkin.add_log_based_on_employee_field": "cvsu_hris.cvsu_hris.overrides.events.employee_checkin.add_log_based_on_employee_field"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "cvsu_hris.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["cvsu_hris.utils.before_request"]
# after_request = ["cvsu_hris.utils.after_request"]

# Job Events
# ----------
# before_job = ["cvsu_hris.utils.before_job"]
# after_job = ["cvsu_hris.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"cvsu_hris.auth.validate"
# ]
