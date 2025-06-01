import { PUBLIC_BACKEND_URL } from '$env/static/public';

import { fail } from "@sveltejs/kit";
import { redirect } from "@sveltejs/kit";

import type { Actions, PageServerLoad } from "./$types";


export const load: PageServerLoad = async (event) => {
    // need to check if token is still valid.
    if (event.cookies.get('session')) {
        redirect(301, '/');
    }
};

export const actions: Actions = {
    default: async ({ cookies, request }) => {
        const data = await request.formData();
        const response = await fetch(`${PUBLIC_BACKEND_URL}/token`, {
            method: "POST",
            body: data
        })
        if (!response.ok) {
            return fail(response.status, {
                error: response.statusText,
            });
        }
        const json = await response.json();
        const token = json.access_token;
        cookies.set('session', token, {
            httpOnly: true,
		    sameSite: "lax",
		    expires: new Date(Date.now() + 30 * 60 * 1000), // TODO: hardcoded 30 minutes is not ideal
		    path: "/"
        })
        return {"session": token}
    }
}
