import api from "./api";

export const BorrowService = {
  // user
  createRequest(data) {
    return api.post("/borrow/requests/", data);
  },

  myBorrows() {
    return api.get("/borrow/my/");
  },

  // getMyRequests() {
  //   return api.get("/borrow/my/");
  // },

  requestReturn(id) {
    return api.post(`/borrow/request-return/${id}/`);
  },

  // admin
  adminList() {
    return api.get("/borrow/admin/requests/");
  },

  // getAdminRequests() {
  //   return api.get("/borrow/admin/requests/");
  // },

  approve(id) {
    return api.post(`/borrow/admin/${id}/approve/`);
  },

  reject(id) {
    return api.post(`/borrow/admin/${id}/reject/`);
  },

  confirmReturn(id) {
    return api.post(`/borrow/admin/${id}/confirm-return/`);
  },
};
