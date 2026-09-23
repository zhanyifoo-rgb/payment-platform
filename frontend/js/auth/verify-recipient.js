import { getRecipient } from "../api/auth.js";
import { goTo } from "../ui/goto.js";

export async function verifyRecipient(state, elements) {

    const accountNumberInput =
        document.getElementById("recipientSearch");

    try {

        const data = await getRecipient(accountNumberInput.value);

        state.name = `${data.firstname} ${data.lastname}`;
        state.accountNumber = data.account_number;

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
