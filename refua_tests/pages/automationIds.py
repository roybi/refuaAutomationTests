"""Meditik Automation IDs (`data-testid`) — source: element mapping doc.

Format: meditik-[page/section]-[element-type]-[description]
Attribute: data-testid
"""


class MeditikIds:
    """Static / prefix constants for get_by_test_id / locator filters."""

    # --- Navbar ---
    NAVBAR_TOOLBAR = "meditik-navbar-toolbar"
    NAVBAR_BTN_HAMBURGER = "meditik-navbar-btn-hamburger"
    NAVBAR_BTN_BACK = "meditik-navbar-btn-back"
    NAVBAR_BTN_HOME = "meditik-navbar-btn-home"
    NAVBAR_BTN_LOGO = "meditik-navbar-btn-logo"
    NAVBAR_BTN_CLOSE_MENU = "meditik-navbar-btn-close-menu"
    NAVBAR_DRAWER_MENU = "meditik-navbar-drawer-menu"
    NAVBAR_BTN_ADMIN_ANNOUNCEMENTS = "meditik-navbar-btn-admin-announcements"
    NAVBAR_BTN_DEBUG_SOLDIER = "meditik-navbar-btn-debug-soldier"
    NAVBAR_BTN_INSTALL = "meditik-navbar-btn-install"
    NAVBAR_BTN_SHARE = "meditik-navbar-btn-share"
    NAVBAR_BTN_LOGOUT = "meditik-navbar-btn-logout"
    NAVBAR_MENU_ITEM_PREFIX = "meditik-navbar-menu-item-"
    NAVBAR_BTN_COMMON_PREFIX = "meditik-navbar-btn-common-"

    # Stable menu destinations (ids from live env / mapping). Label text is soft.
    MENU_ITEM_MY_APPOINTMENTS = "meditik-navbar-menu-item-1"
    MENU_ITEM_LAB_RESULTS = "meditik-navbar-menu-item-2"
    MENU_ITEM_MEDICINES = "meditik-navbar-menu-item-3"
    MENU_ITEM_REFERRALS = "meditik-navbar-menu-item-4"
    MENU_ITEM_EXEMPTIONS = "meditik-navbar-menu-item-5"
    MENU_ITEM_SICK_DAYS = "meditik-navbar-menu-item-6"
    MENU_ITEM_VACCINATIONS = "meditik-navbar-menu-item-7"
    MENU_ITEM_VISIT_SUMMARIES = "meditik-navbar-menu-item-8"
    MENU_ITEM_MEDICAL_PROFILE = "meditik-navbar-menu-item-12"
    MENU_ITEM_MY_REQUESTS = "meditik-navbar-menu-item-14"
    MENU_COMMON_BOOK_APPOINTMENT = "meditik-navbar-btn-common-15"
    MENU_COMMON_URGENT_CARE = "meditik-navbar-btn-common-23"
    MENU_COMMON_SEND_DOCTOR_REQUEST = "meditik-navbar-btn-common-29"

    # --- Home ---
    HOME_PAGE = "meditik-home-page"
    HOME_BTN_APPOINTMENTS = "meditik-home-btn-appointments"
    HOME_BTN_FUTURE_APPOINTMENTS_WIDGET = "meditik-home-btn-future-appointments-widget"
    HOME_BTN_LAB_RESULTS = "meditik-home-btn-lab-results"
    HOME_BTN_MEDICINES = "meditik-home-btn-medicines"
    HOME_BTN_MEDICINES_WIDGET = "meditik-home-btn-medicines-widget"
    HOME_BTN_REFERRALS = "meditik-home-btn-referrals"
    HOME_BTN_REFERRALS_WIDGET = "meditik-home-btn-referrals-widget"
    HOME_BTN_SICK_DAYS = "meditik-home-btn-sick-days"
    HOME_BTN_EXEMPTIONS = "meditik-home-btn-exemptions"
    HOME_BTN_EXEMPTIONS_WIDGET = "meditik-home-btn-exemptions-home-page"
    HOME_BTN_VACCINATIONS = "meditik-home-btn-vaccinations"
    HOME_BTN_MEDICAL_PROFILE = "meditik-home-btn-medical-profile"
    HOME_BTN_URGENT_CARE = "meditik-home-btn-urgent-care"
    HOME_BTN_ALL_ACTIONS = "meditik-home-btn-all-actions"
    HOME_BTN_ZIMUN_TORIM = "meditik-home-btn-zimun-torim"
    HOME_BTN_USER_REQUESTS = "meditik-home-btn-user-requests"
    HOME_BTN_USER_REQUESTS_WIDGET = "meditik-home-btn-user-requests-widget"
    HOME_BTN_ANNOUNCEMENTS = "meditik-home-btn-announcements"
    # Last-update control on home footer — no data-testid in mapping yet.
    # Located via version.svg icon + Hebrew label in home_page_meditek.py.

    # --- All Actions ---
    ALL_ACTIONS_PAGE = "meditik-all-actions-page"
    ALL_ACTIONS_INPUT_SEARCH = "meditik-all-actions-input-search"

    # --- Appointments / ZimunTorim ---
    APPOINTMENTS_PAGE = "meditik-appointments-page"
    APPOINTMENTS_TAB_UPCOMING = "meditik-appointments-tab-upcoming"
    APPOINTMENTS_TAB_HISTORY = "meditik-appointments-tab-history"
    APPOINTMENTS_TAB_WAITING_LIST = "meditik-appointments-tab-waiting-list"
    APPOINTMENTS_BTN_MAKE = "meditik-appointments-btn-make-appointment"
    APPOINTMENTS_ROW_PREFIX = "meditik-appointments-row-"
    APPOINTMENTS_BTN_CANCEL_PREFIX = "meditik-appointments-btn-cancel-"

    # --- Lab Results ---
    LAB_RESULTS_PAGE = "meditik-lab-results-page"
    LAB_RESULTS_TAB_REGULAR = "meditik-lab-results-tab-regular"
    LAB_RESULTS_TAB_CULTURE = "meditik-lab-results-tab-culture"
    LAB_RESULTS_TAB_IMAGING = "meditik-lab-results-tab-imaging"
    LAB_RESULTS_ROW_PREFIX = "meditik-lab-results-row-"
    LAB_RESULTS_BTN_DETAILS_PREFIX = "meditik-lab-results-btn-details-"

    # --- Medicines & Prescriptions (תרופות ומרשמים) — tabbed /medicines page ---
    # Source: MediTik_Medicines_Prescriptions_BDD_E2E_TestCases workbook
    # (MEDICINES-001..024). Three categories: My Prescriptions (active),
    # Permanent Medicines, Previous Prescriptions (expired).
    # NOTE: the workbook defines empty-state elements ONLY for My Prescriptions.
    MEDICINES_TABBED_PATH = "/medicines"
    MEDICINES_TABS_HEADER = "meditik-tabs-header"
    MEDICINES_TAB_ACTIVE = "active-medicines-tab"
    MEDICINES_TAB_PERMANENT = "permanent-medicines-tab"
    MEDICINES_TAB_EXPIRED = "expired-medicines-tab"
    MEDICINES_PANEL_ACTIVE = "meditik-tabs-panel-active-medicines"
    MEDICINES_PANEL_PERMANENT = "meditik-tabs-panel-permanent-medicines"
    MEDICINES_PANEL_EXPIRED = "meditik-tabs-panel-expired-medicines"
    # Tab-strip scroll affordances (referenced by clarification-pending cases).
    MEDICINES_TAB_SCROLL_RIGHT_ICON = "KeyboardArrowRightIcon"
    MEDICINES_TAB_SCROLL_LEFT_ICON = "KeyboardArrowLeftIcon"

    # --- Medicines ---
    MEDICINES_PAGE = "meditik-medicines-page"
    MEDICINES_ROW_PREFIX = "meditik-medicines-row-"
    MEDICINES_BTN_DETAILS_PREFIX = "meditik-medicines-btn-details-"

    # --- Referrals (הפניות) — tabbed /referrals page ---
    # Source: MediTik_Referrals_BDD_E2E_TestCases workbook (REFERRALS-001..024).
    # My Referrals / Waiting for Approval / Past Referrals tabs + a shared
    # empty state that MUST be scoped to the active panel (REFERRALS-024).
    REFERRALS_TABBED_PATH = "/referrals"
    REFERRALS_TABS_HEADER = "meditik-tabs-header"
    REFERRALS_TAB_MINE = "my-referrals-tab"
    REFERRALS_TAB_WAITING_APPROVAL = "referrals-waiting-for-approval-tab"
    REFERRALS_TAB_PAST = "past-referrals-tab"
    REFERRALS_PANEL_MINE = "meditik-tabs-panel-my-referrals"
    REFERRALS_PANEL_WAITING_APPROVAL = (
        "meditik-tabs-panel-referrals-waiting-for-approval"
    )
    REFERRALS_PANEL_PAST = "meditik-tabs-panel-past-referrals"

    # --- Referrals ---
    REFERRALS_PAGE = "meditik-referrals-page"
    REFERRALS_ROW_PREFIX = "meditik-referrals-row-"
    REFERRALS_BTN_DETAILS_PREFIX = "meditik-referrals-btn-details-"
    REFERRALS_BTN_SUPPLIER_CHANGE_PREFIX = "meditik-referrals-btn-supplier-change-"

    # --- Sick Days (ימי מחלה) — /sick-days module page ---
    # Source: Sick_days workbook (SICK-DAYS-001..020). This page is NOT tabbed:
    # its coverage centres on a page-level empty state that must resolve to
    # exactly one match. SICK-DAYS-002 specifies the exact Hebrew copy and its
    # Error/Validation column requires failing when the text differs, so unlike
    # the English-copy workbooks this string is a HARD assertion.
    SICK_DAYS_MODULE_PATH = "/sick-days"
    SICK_DAYS_EMPTY_STATE_TITLE = "meditik-empty-state-title"
    SICK_DAYS_EMPTY_STATE_ICON = "meditik-empty-state-icon"
    SICK_DAYS_EXPECTED_EMPTY_TEXT = "ימי מחלה שיתקבלו עבורך יופיעו כאן"

    # --- Sick Days ---
    SICK_DAYS_PAGE = "meditik-sick-days-page"
    SICK_DAYS_ROW_PREFIX = "meditik-sick-days-row-"
    SICK_DAYS_BTN_DOWNLOAD_PREFIX = "meditik-sick-days-btn-download-"

    # --- Exemptions ---
    EXEMPTIONS_PAGE = "meditik-exemptions-page"
    EXEMPTIONS_ROW_PREFIX = "meditik-exemptions-row-"
    EXEMPTIONS_BTN_DETAILS_PREFIX = "meditik-exemptions-btn-details-"

    # --- Vaccinations (חיסונים) — /vaccinations module page ---
    # Source: Vaccinations workbook (VACC-001..020). Case-for-case twin of the
    # Sick_days workbook: same non-tabbed empty-state shape, same Ready set,
    # same "fail if duplicated or hidden" rules. Shares the empty-state testids
    # and is implemented as a configuration of EmptyStateModulePage.
    VACCINATIONS_MODULE_PATH = "/vaccinations"
    VACCINATIONS_EXPECTED_EMPTY_TEXT = "חיסונים שביצעת יופיעו כאן"

    # --- Vaccinations ---
    VACCINATIONS_PAGE = "meditik-vaccinations-page"
    VACCINATIONS_ROW_PREFIX = "meditik-vaccinations-row-"

    # --- Medical Profile ---
    MEDICAL_PROFILE_PAGE = "meditik-medical-profile-page"

    # --- Urgent Care ---
    URGENT_CARE_PAGE = "meditik-urgent-care-page"
    URGENT_CARE_BTN_START = "meditik-urgent-care-btn-start"

    # --- My Requests (הבקשות שלי) — tabbed /user-requests page ---
    # Source: My_Requset_Test_cases.xlsx (elements.json grounded). These ids
    # describe the tabbed "My Requests" screen (New / Approved / Declined) and
    # its shared empty-state, distinct from the legacy action page below.
    MY_REQUESTS_PATH = "/user-requests"

    # Navbar (shared shell) — reused here for My Requests coverage.
    MY_REQUESTS_NAVBAR_TOOLBAR = "meditik-navbar-toolbar"
    MY_REQUESTS_NAVBAR_BTN_HAMBURGER = "meditik-navbar-btn-hamburger"
    MY_REQUESTS_NAVBAR_IMG_HAMBURGER = "meditik-navbar-img-hamburger"
    MY_REQUESTS_NAVBAR_BTN_LOGO = "meditik-navbar-btn-logo"
    MY_REQUESTS_NAVBAR_IMG_LOGO = "meditik-navbar-img-logo"
    MY_REQUESTS_NAVBAR_TABS_PORTAL = "meditik-navbar-tabs-portal"

    # Tabs header + per-status tabs and their panels.
    MY_REQUESTS_TABS_HEADER = "meditik-tabs-header"
    MY_REQUESTS_TAB_ACTIVE = "active-requests-tab"
    MY_REQUESTS_TAB_APPROVED = "approved-requests-tab"
    MY_REQUESTS_TAB_DECLINED = "declined-requests-tab"
    MY_REQUESTS_PANEL_ACTIVE = "meditik-tabs-panel-active-requests"
    MY_REQUESTS_PANEL_APPROVED = "meditik-tabs-panel-approved-requests"
    MY_REQUESTS_PANEL_DECLINED = "meditik-tabs-panel-declined-requests"

    # Virtual list card locator template. The mapping captured it as
    # "0-user-requests-list-{index}"; ``{index}`` is substituted per card and
    # the leading segment is the panel/virtual-list group.
    MY_REQUESTS_LIST_CARD_TEMPLATE = "0-user-requests-list-{index}"
    MY_REQUESTS_LIST_CARD_PREFIX = "0-user-requests-list-"

    # Scoped empty state (shared component — must be scoped to the active panel).
    MY_REQUESTS_EMPTY_STATE_ICON = "meditik-empty-state-icon"
    MY_REQUESTS_EMPTY_STATE_TITLE = "meditik-empty-state-title"
    MY_REQUESTS_EMPTY_STATE_LINK = "meditik-empty-state-link"

    # Home widget for My Requests.
    MY_REQUESTS_HOME_PAGE = "meditik-home-page"
    MY_REQUESTS_HOME_BTN_WIDGET = "meditik-home-btn-user-requests-widget"
    MY_REQUESTS_HOME_WIDGET_ARROW = "meditik-home-widget-arrow-user-requests-widget"
    MY_REQUESTS_WIDGET_EMPTY_STATE = "user-requests-widget-empty-state"
    MY_REQUESTS_WIDGET_EMPTY_STATE_EXTRA_INFO = (
        "meditik-card-user-requests-widget-empty-state-extra-info"
    )

    # Speed dial (quick actions) on My Requests.
    MY_REQUESTS_SPEED_DIAL_TRIGGER = "meditik-speed-dial-btn-trigger"
    MY_REQUESTS_SPEED_DIAL_FAB = "meditik-speed-dial-btn-fab"
    MY_REQUESTS_SPEED_DIAL_ADD_ICON = "AddIcon"

    # --- My Appointments (התורים שלי) — tabbed /zimun-torim page ---
    # Source: My Appointments workbook (APPT-001..034, elements.json grounded).
    # Upcoming / Waiting Lists / Past Appointments tabs + shared empty state,
    # a Past-appointments card list, a filter entry and a booking link.
    MY_APPOINTMENTS_PATH = "/zimun-torim"
    MY_APPOINTMENTS_PAGE = "meditik-appointments-page"

    # Tabs header + per-category tabs and their panels. NOTE: the Upcoming tab
    # reuses the shared active-requests testids (confirmed in the workbook).
    MY_APPOINTMENTS_TABS_HEADER = "meditik-tabs-header"
    MY_APPOINTMENTS_TAB_UPCOMING = "active-requests-tab"
    MY_APPOINTMENTS_TAB_WAITING_LISTS = "waiting-lists-tab"
    MY_APPOINTMENTS_TAB_PAST = "past-appointments-tab"
    MY_APPOINTMENTS_PANEL_UPCOMING = "meditik-tabs-panel-active-requests"
    MY_APPOINTMENTS_PANEL_WAITING_LISTS = "meditik-tabs-panel-waiting-lists"
    MY_APPOINTMENTS_PANEL_PAST = "meditik-tabs-panel-past-appointments"

    # Past-appointments virtual list card + its extra-info card.
    MY_APPOINTMENTS_PAST_CARD_TEMPLATE = "past-appointments-list-{index}"
    MY_APPOINTMENTS_PAST_CARD_PREFIX = "past-appointments-list-"
    MY_APPOINTMENTS_PAST_CARD_EXTRA_INFO_TEMPLATE = (
        "meditik-card-past-appointments-list-{index}-extra-info"
    )

    # Booking entry + filter (clarification-pending behaviour, ids are grounded).
    MY_APPOINTMENTS_LINK_BOOK = "meditik-appointments-link-book-appointment"
    MY_APPOINTMENTS_FILTER_BTN_OPEN = "meditik-filter-btn-open"
    MY_APPOINTMENTS_FILTER_LABEL = "meditik-filter-label"

    # Home future-appointments widget.
    MY_APPOINTMENTS_HOME_BTN_WIDGET = "meditik-home-btn-future-appointments-widget"
    MY_APPOINTMENTS_HOME_WIDGET_ARROW = (
        "meditik-home-widget-arrow-future-appointments-widget"
    )
    MY_APPOINTMENTS_WIDGET_EMPTY_STATE = "future-appointments-widget-empty-state"
    MY_APPOINTMENTS_WIDGET_EMPTY_STATE_EXTRA_INFO = (
        "meditik-card-future-appointments-widget-empty-state-extra-info"
    )

    # --- User Requests ---
    USER_REQUESTS_PAGE = "meditik-user-requests-page"
    USER_REQUESTS_BTN_PRESCRIPTION = "meditik-user-requests-btn-prescription"
    USER_REQUESTS_BTN_REFERRAL = "meditik-user-requests-btn-referral"
    USER_REQUESTS_BTN_SICK_DAYS = "meditik-user-requests-btn-sick-days"
    USER_REQUESTS_BTN_GLASSES = "meditik-user-requests-btn-glasses-voucher"
    USER_REQUESTS_BTN_DENTIST = "meditik-user-requests-btn-dentist"
    USER_REQUESTS_BTN_INSOLES = "meditik-user-requests-btn-insoles"
    USER_REQUESTS_BTN_REFERRAL_ANSWERS = "meditik-user-requests-btn-referral-answers"
    USER_REQUESTS_BTN_RETROACTIVE = "meditik-user-requests-btn-retroactive-commitment"
    USER_REQUESTS_ROW_PREFIX = "meditik-user-requests-row-"

    # --- Announcements ---
    ANNOUNCEMENTS_PAGE = "meditik-announcements-page"
    ANNOUNCEMENTS_BTN_ADD = "meditik-announcements-btn-add"
    ANNOUNCEMENTS_ROW_PREFIX = "meditik-announcements-row-"

    # --- Feedback ---
    FEEDBACK_BTN_OPEN = "meditik-feedback-btn-open"
    FEEDBACK_MODAL = "meditik-feedback-modal"
    FEEDBACK_INPUT_RATING = "meditik-feedback-input-rating"
    FEEDBACK_INPUT_TEXT = "meditik-feedback-input-text"
    FEEDBACK_BTN_SUBMIT = "meditik-feedback-btn-submit"
    FEEDBACK_BTN_CLOSE = "meditik-feedback-btn-close"

    # --- Filter ---
    FILTER_BTN_OPEN = "meditik-filter-btn-open"
    FILTER_BTN_CLEAR = "meditik-filter-btn-clear"
    FILTER_BTN_CONFIRM = "meditik-filter-btn-confirm"
    FILTER_BTN_OPTION_PREFIX = "meditik-filter-btn-option-"

    # --- Speed Dial ---
    SPEED_DIAL_TRIGGER = "meditik-speed-dial-btn-trigger"
    SPEED_DIAL_ACTION_PREFIX = "meditik-speed-dial-btn-"
    # Stable action ids (numeric) observed on test env
    SPEED_DIAL_BOOK_APPOINTMENT = "meditik-speed-dial-btn-15"
    SPEED_DIAL_SICK_DAYS = "meditik-speed-dial-btn-16"
    SPEED_DIAL_NEW_REFERRAL = "meditik-speed-dial-btn-18"
    SPEED_DIAL_PRESCRIPTION = "meditik-speed-dial-btn-20"
    SPEED_DIAL_INSOLES = "meditik-speed-dial-btn-21"
    SPEED_DIAL_REFERRAL_ANSWER = "meditik-speed-dial-btn-22"
    SPEED_DIAL_BARHAN = "meditik-speed-dial-btn-30"
    SPEED_DIAL_MOKED = "meditik-speed-dial-btn-43"

    # --- PWA ---
    DOWNLOAD_PWA_MODAL = "meditik-download-pwa-modal"
    DOWNLOAD_PWA_BTN_CLOSE = "meditik-download-pwa-btn-close"
    DOWNLOAD_PWA_BTN_DOWNLOAD = "meditik-download-pwa-btn-download"
    DOWNLOAD_PWA_TOGGLE_DONT_SHOW = "meditik-download-pwa-toggle-dont-show"

    # --- Navigation apps ---
    NAVIGATION_BTN_OPEN = "meditik-navigation-btn-open"
    NAVIGATION_BTN_WAZE = "meditik-navigation-btn-waze"
    NAVIGATION_BTN_GOOGLE_MAPS = "meditik-navigation-btn-google-maps"
    NAVIGATION_BTN_MOOVIT = "meditik-navigation-btn-moovit"

    # --- Shared ---
    INPUT_PHONE_NUMBER = "meditik-input-phone-number"
    PREV_NEXT_BTN_BACK = "meditik-prev-next-btn-back"
    PREV_NEXT_BTN_NEXT = "meditik-prev-next-btn-next"
    POPUP_MODAL_PREFIX = "meditik-popup-modal-"
    POPUP_BTN_CONFIRM_PREFIX = "meditik-popup-btn-confirm-"
    POPUP_BTN_CANCEL_PREFIX = "meditik-popup-btn-cancel-"
    POPUP_BTN_CLOSE_PREFIX = "meditik-popup-btn-close-"
