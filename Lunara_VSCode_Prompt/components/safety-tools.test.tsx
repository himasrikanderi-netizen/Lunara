// @vitest-environment jsdom
import {cleanup,fireEvent,render,screen,waitFor} from "@testing-library/react";
import {afterEach,beforeEach,expect,it,vi} from "vitest";
import Safety from "../app/safety/page";
const {fetchSafePlaces}=vi.hoisted(()=>({fetchSafePlaces:vi.fn()}));
vi.mock("@/lib/api",()=>({fetchSafePlaces}));
beforeEach(()=>{localStorage.clear();fetchSafePlaces.mockReset()});
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it("stores a trusted contact with phone and allows removal",()=>{
 render(<Safety/>);
 fireEvent.change(screen.getByLabelText("Contact name"),{target:{value:"Asha"}});
 fireEvent.change(screen.getByLabelText("Phone number"),{target:{value:"+91 9876543210"}});
 fireEvent.click(screen.getByText("Add contact"));
 expect(screen.getByText("Asha")).toBeTruthy();
 expect(screen.getByRole("link",{name:/Call/}).getAttribute("href")).toBe("tel:+919876543210");
 expect(JSON.parse(localStorage.getItem("lunara-trusted-contacts")??"[]")).toHaveLength(1);
 fireEvent.click(screen.getByRole("button",{name:"Remove Asha"}));
 expect(JSON.parse(localStorage.getItem("lunara-trusted-contacts")??"[]")).toHaveLength(0);
});
it("sets, resets, and cancels a check-in deadline",()=>{
 render(<Safety/>);
 fireEvent.click(screen.getByText("Set check-in for 30 minutes"));
 const first=Number(localStorage.getItem("lunara-check-in-deadline"));
 expect(first).toBeGreaterThan(Date.now());
 fireEvent.click(screen.getByText("Reset to 30 minutes"));
 expect(Number(localStorage.getItem("lunara-check-in-deadline"))).toBeGreaterThanOrEqual(first);
 fireEvent.click(screen.getByText("Cancel timer"));
 expect(localStorage.getItem("lunara-check-in-deadline")).toBeNull();
});
it("uses manual coordinates for nearby mapped hospitals",async()=>{
 fetchSafePlaces.mockResolvedValue({places:[{id:"node/1",category:"hospital",name:"Mapped Hospital",location:{lat:17.42,lng:78.52},distance_m:1200,osm_url:"https://www.openstreetmap.org/node/1"}],data_status:"Mapped search results only",source:"OpenStreetMap"});
 render(<Safety/>);
 fireEvent.change(screen.getByLabelText("Manual location (optional latitude, longitude)"),{target:{value:"17.411568, 78.527463"}});
 fireEvent.click(screen.getAllByText("Find nearby")[0]);
 await waitFor(()=>expect(screen.getByText("Mapped Hospital")).toBeTruthy());
 expect(fetchSafePlaces).toHaveBeenCalledWith({lat:17.411568,lng:78.527463},"hospital");
 expect(screen.getByRole("link",{name:"Navigate"}).getAttribute("href")).toContain("google.com/maps/dir");
});
