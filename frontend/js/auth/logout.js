export async function handleSignOut() {
    sessionStorage.removeItem("access_token");
    window.location.href = "./login.html";
}