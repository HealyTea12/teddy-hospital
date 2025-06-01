import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = ( event ) => {
    if (!event.cookies.get('session') && !event.url.pathname.startsWith('/login')) {
        redirect(301, '/login');
    }
}