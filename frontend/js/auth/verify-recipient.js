import { getRecipient } from "../api/auth.js";
import { goTo, initials } from "../ui/goto.js";

export async function verifyRecipient(state, elements) {

    const accountNumberInput =
        document.getElementById("recipientSearch");

    try {

        const data = await getRecipient(state.accountNumber);
        state.name = `${data.first_name} ${data.last_name}`;
        state.accountNumber = data.account_number;
        state.detail = data.account_number;
        document.getElementById("pillAvatar").textContent = initials(state.name);
        document.getElementById("pillName").textContent = state.name;
        document.getElementById("pillDetail").textContent = data.account_number;

        goTo(2, state, elements);

    } catch (error) {

        console.error(error);

        const errorElement = document.getElementById("recipientSearch-err");
        console.log(error.status)
        switch (error.status) {
            case 400:
                errorElement.textContent =
                    "You cannot send money to yourself";
                break;

            case 404:
                errorElement.textContent =
                    "Recipient not found";
                break;

            case 401:
                window.location.href = "./login.html";
                return;

            default:
                errorElement.textContent =
                    "Something went wrong. Please try again.";
        }

        errorElement.setAttribute("data-shown", "true");

    }

}
