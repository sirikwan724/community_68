import { createRouter, createWebHistory } from "vue-router";

// Layouts
import MainLayout from "../layouts/MainLayout.vue";
import AdminLayout from "../layouts/AdminLayout.vue";

// Pages
import HomePage from "../pages/HomePage.vue";
import LoginPage from "../pages/LoginPage.vue";
import RegisterRequestPage from "../pages/RegisterRequestPage.vue";

import ProfilePage from "../pages/ProfilePage.vue";
import ReportForm from "../pages/ReportForm.vue";

import AdminDashboard from "../pages/admin/AdminDashboard.vue";
import UserApprovePage from "../pages/admin/UserApprovePage.vue";
import AdminProfilePage from "../pages/admin/AdminProfilePage.vue";
import AdminNewsCreate from "../pages/admin/AdminNewsCreate.vue";
import AdminNewsEdit from "../pages/admin/AdminNewsEdit.vue";
import AdminNewsList from "../pages/admin/AdminNewsList.vue";
import AdminStats from "../pages/admin/AdminStats.vue";

import NotFoundPage from "../pages/NotFoundPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // =============================================
    // Public Routes (คนทั่วไปเข้าได้)
    // =============================================
    {
      path: "/login",
      component: LoginPage,
      meta: { guestOnly: true }
    },
    {
      path: "/register-request",
      component: RegisterRequestPage,
      meta: { guestOnly: true }
    },

    // =============================================
    // Admin Zone (ใช้ AdminLayout)
    // =============================================
    {
      path: "/admin",
      component: AdminLayout,
      meta: { requiresAuth: true, adminOnly: true },
      children: [
        { path: "dashboard", component: AdminDashboard },
        { path: "users/approve", component: UserApprovePage },
        { path: "profile", component: AdminProfilePage },
        { path: "news/create", component: AdminNewsCreate },
        { path: "news/:id/edit", component: AdminNewsEdit },
        { path: "news-list", component: AdminNewsList },
        { path: "reports", component: () => import("../pages/admin/AdminReports.vue"),},
        // { path: "/admin/reports", component: () => import("../pages/admin/AdminReports.vue"),},
        { path: "/admin/reports-processing", component: () => import("../pages/admin/AdminProcessingReports.vue"),},
        { path: "/admin/reports-resolved", component: () => import("../pages/admin/AdminResolvedReports.vue"),},
        { path: "/admin/helps", component: () => import("../pages/admin/AdminRequestHelp.vue"),},
                // 🟥 Admin — จัดการบริการสาธารณะ
        { path: "services", component: () => import("../pages/admin/AdminServiceList.vue"),},
        { path: "services/create", component: () => import("../pages/admin/AdminServiceCreate.vue"),},
        { path: "services/:id/edit", component: () => import("../pages/admin/AdminServiceEdit.vue"),},
        { path: "/admin/stats", name: "AdminStats", component: AdminStats, meta: { requiresAuth: true, adminOnly: true }},
        { path: "/admin/appointments", name: "admin-appointments", component: () => import("../pages/admin/AdminAppointmentList.vue"),},
        { path: "/admin/borrows", name: "AdminBorrows", component: () => import("../pages/admin/BorrowAdmin.vue"),meta: { requiresAuth: true, role: "admin" },},
        { path: "village/info", component: () => import("../pages/admin/village/AdminVillageInfo.vue"),},
        { path: "village/fund", component: () => import("../pages/admin/village/AdminVillageFund.vue"),},
        { path: "profiles", component: () => import("../pages/admin/village/AdminCommunityProfiles.vue"),},
        { path: "profiles/create", component: () => import("../pages/admin/village/AdminCommunityProfileForm.vue"),},
        { path: "profiles/:id/edit", component: () => import("../pages/admin/village/AdminCommunityProfileForm.vue"),},
      ],
    },

    // =============================================
    // User Zone (MainLayout)
    // =============================================
    {
      path: "/",
      component: MainLayout,
      children: [
        { path: "", component: HomePage },

        {
          path: "/village",
          component: () => import("@/pages/village/VillagePage.vue")
        },

        {
          path: "profile",
          component: ProfilePage,
          meta: { requiresAuth: true },
        },

        {
          path: "report/create",
          component: ReportForm,
          meta: { requiresAuth: true },
        },
         
        {
          path: "report/list",
          component: () => import("../pages/ReportListPage.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: "report/edit/:id",
          component: () => import("../pages/ReportEdit.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: "/request-help",
          component: () => import("../pages/RequestHelpForm.vue"),
        },
        {
          path: '/news/:id',
          name: 'news-detail',
          component: () => import('../pages/News/NewsDetail.vue'),
        },
                // บริการสาธารณะ (ผู้เยี่ยมชม + ผู้ใช้)
        {
          path: "my-history",
          component: () => import("../pages/MyHistory.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: "edit-request/:id",
          component: () => import("../pages/EditRequest.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: "public-services",
          component: () => import("../pages/publicservice/PublicServiceList.vue")
        },
        {
          path: "public-services/:id",
          component: () => import("../pages/publicservice/PublicServiceDetail.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: "/appointment/create",
          component: () => import("../pages/AppointmentForm.vue"),
        },
        {
          path: "/appointment/my",
          component: () => import("../pages/MyAppointments.vue"),
        },
        {
          path: "/appointments/edit/:id",
          component: () => import("../pages/EditAppointment.vue"),
        },
        {
          path: "borrow",
          component: () => import("../pages/borrow/BorrowForm.vue"),
          meta: { requiresAuth: true },
        },
      ],
    },

    // =============================================
    // 404
    // =============================================
    {
      path: "/:pathMatch(.*)*",
      component: NotFoundPage,
    },
  ],
});

// =============================================
// Route Guard
// =============================================
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("access");
  const role = localStorage.getItem("role");

  // ต้องล็อกอิน
  if (to.meta.requiresAuth && !token) {
    return next("/login");
  }

  // เฉพาะ Admin
  if (to.meta.adminOnly && role !== "admin") {
    return next("/");
  }

  next();
});

export default router;
