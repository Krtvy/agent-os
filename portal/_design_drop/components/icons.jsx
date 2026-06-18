/* global React */
/* ============================================================
   Rootlabs Portal — Icons (monochrome, 16px nominal)
   Each icon is a stateless functional component.
   Pass {size, className} to override.
   ============================================================ */

const Icon = ({ children, size = 16, className, style }) => (
  <svg
    width={size} height={size} viewBox="0 0 16 16"
    fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
    className={className} style={style} aria-hidden="true"
  >{children}</svg>
);

const IVideo = (p) => <Icon {...p}><rect x="1.5" y="3" width="9" height="10" rx="1.5"/><path d="M10.5 6.5l4-2v7l-4-2z"/></Icon>;
const ILive  = (p) => <Icon {...p}><circle cx="8" cy="8" r="2.5" fill="currentColor" stroke="none"/><circle cx="8" cy="8" r="5"/><circle cx="8" cy="8" r="7" opacity=".4"/></Icon>;
const ICart  = (p) => <Icon {...p}><path d="M2 3h2l1.6 8.2a1 1 0 0 0 1 .8h5.4a1 1 0 0 0 1-.78L14.5 6h-9"/><circle cx="6.5" cy="13.5" r=".75" fill="currentColor"/><circle cx="11.5" cy="13.5" r=".75" fill="currentColor"/></Icon>;
const IRupee = (p) => <Icon {...p}><path d="M4.5 3.5h7M4.5 6h7M4.5 8.5h2.5a3 3 0 0 0 0-5M4.5 8.5l4.5 4"/></Icon>;
const IPercent = (p) => <Icon {...p}><circle cx="4.5" cy="4.5" r="1.5"/><circle cx="11.5" cy="11.5" r="1.5"/><path d="M13 3 3 13"/></Icon>;
const IUp    = (p) => <Icon {...p}><path d="M3 10l5-5 5 5"/></Icon>;
const IDown  = (p) => <Icon {...p}><path d="M3 6l5 5 5-5"/></Icon>;
const IArrowRight = (p) => <Icon {...p}><path d="M3 8h10M9 4l4 4-4 4"/></Icon>;
const IChevron = (p) => <Icon {...p}><path d="M6 4l4 4-4 4"/></Icon>;
const IChevronDown = (p) => <Icon {...p}><path d="M4 6l4 4 4-4"/></Icon>;
const ISearch = (p) => <Icon {...p}><circle cx="7" cy="7" r="4.5"/><path d="M14 14l-3.5-3.5"/></Icon>;
const IFilter = (p) => <Icon {...p}><path d="M2 3h12l-4.5 5.5V13l-3-1.5V8.5L2 3z"/></Icon>;
const ICalendar = (p) => <Icon {...p}><rect x="2" y="3.5" width="12" height="10" rx="1.5"/><path d="M2 6.5h12M5 2v3M11 2v3"/></Icon>;
const IPlus = (p) => <Icon {...p}><path d="M8 3v10M3 8h10"/></Icon>;
const IX = (p) => <Icon {...p}><path d="M4 4l8 8M12 4l-8 8"/></Icon>;
const IDownload = (p) => <Icon {...p}><path d="M8 2v8m0 0l-3-3m3 3l3-3M3 13h10"/></Icon>;
const IUpload = (p) => <Icon {...p}><path d="M8 13V5m0 0L5 8m3-3 3 3M3 2h10"/></Icon>;
const IMore = (p) => <Icon {...p}><circle cx="3.5" cy="8" r=".8" fill="currentColor"/><circle cx="8" cy="8" r=".8" fill="currentColor"/><circle cx="12.5" cy="8" r=".8" fill="currentColor"/></Icon>;
const IExternal = (p) => <Icon {...p}><path d="M6 3H3v10h10v-3M9 2h5v5M14 2 8 8"/></Icon>;
const ICheck = (p) => <Icon {...p}><path d="M3 8l3.5 3.5L13 5"/></Icon>;
const IExpand = (p) => <Icon {...p}><path d="M3 6V3h3M13 6V3h-3M3 10v3h3M13 10v3h-3"/></Icon>;
const IUser = (p) => <Icon {...p}><circle cx="8" cy="5.5" r="2.5"/><path d="M3 13.5c.8-2.4 2.7-3.5 5-3.5s4.2 1.1 5 3.5"/></Icon>;
const IUsers = (p) => <Icon {...p}><circle cx="6" cy="6" r="2.2"/><circle cx="11.5" cy="7" r="1.7"/><path d="M2 13c.6-2 2-3 4-3s3.4 1 4 3M10 13c.4-1.5 1.4-2.3 3-2.3"/></Icon>;
const IGrid = (p) => <Icon {...p}><rect x="2.5" y="2.5" width="4.5" height="4.5" rx=".5"/><rect x="9" y="2.5" width="4.5" height="4.5" rx=".5"/><rect x="2.5" y="9" width="4.5" height="4.5" rx=".5"/><rect x="9" y="9" width="4.5" height="4.5" rx=".5"/></Icon>;
const IPackage = (p) => <Icon {...p}><path d="M8 2 2 5v6l6 3 6-3V5L8 2z"/><path d="M2 5l6 3 6-3M8 8v6"/></Icon>;
const ITable = (p) => <Icon {...p}><rect x="2" y="3" width="12" height="10" rx="1"/><path d="M2 7h12M2 11h12M6 7v6M10 7v6"/></Icon>;
const ISwitch = (p) => <Icon {...p}><path d="M3 5h9l-2-2M13 11H4l2 2"/></Icon>;
const ILogout = (p) => <Icon {...p}><path d="M9 3H4a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h5M10 5l3 3-3 3M13 8H6"/></Icon>;
const IInfo = (p) => <Icon {...p}><circle cx="8" cy="8" r="6"/><path d="M8 7v4M8 5.2v.1"/></Icon>;
const IStar = (p) => <Icon {...p}><path d="M8 2 9.8 6 14 6.4l-3.2 2.8L11.8 13 8 10.8 4.2 13l1-3.8L2 6.4 6.2 6 8 2z"/></Icon>;
const ISparkles = (p) => <Icon {...p}><path d="M6 2v3M4.5 3.5h3M10 8v3M8.5 9.5h3M5 9l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" transform="translate(2,-2) scale(.7)"/></Icon>;
const IClock = (p) => <Icon {...p}><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 1.5"/></Icon>;
const IList = (p) => <Icon {...p}><circle cx="3" cy="4" r=".7" fill="currentColor"/><circle cx="3" cy="8" r=".7" fill="currentColor"/><circle cx="3" cy="12" r=".7" fill="currentColor"/><path d="M6 4h8M6 8h8M6 12h8"/></Icon>;
const IBolt = (p) => <Icon {...p}><path d="M9 2 4 9h4l-1 5 5-7H8l1-5z"/></Icon>;

Object.assign(window, {
  IVideo, ILive, ICart, IRupee, IPercent,
  IUp, IDown, IArrowRight, IChevron, IChevronDown,
  ISearch, IFilter, ICalendar, IPlus, IX, IDownload, IUpload,
  IMore, IExternal, ICheck, IExpand, IUser, IUsers, IGrid, IPackage,
  ITable, ISwitch, ILogout, IInfo, IStar, ISparkles, IClock, IList, IBolt,
});
